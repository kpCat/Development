"""Offline OOXML inspection. Never executes formulas, SQL, macros or links."""
import argparse
import json
from pathlib import Path
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'m': MAIN}
MAX_ENTRY = 10 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024


def local(tag):
    return tag.rsplit('}', 1)[-1]


def tree_data(element):
    if element is None:
        return {}
    result = dict(element.attrib)
    for child in element:
        key = local(child.tag)
        value = tree_data(child)
        if key in result:
            previous = result[key]
            result[key] = previous + [value] if isinstance(previous, list) else [previous, value]
        else:
            result[key] = value
    return result


def all_text(element):
    return ''.join(node.text or '' for node in element.iter() if local(node.tag) == 't') if element is not None else ''


def resolve_part(owner, target):
    part = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(owner), target))
    if part.startswith('../') or ':' in part or '\\' in part:
        raise ValueError('Небезопасный путь внутри OOXML.')
    return part


def parse_workbook(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 10000 or sum(item.file_size for item in entries) > MAX_TOTAL:
            raise ValueError('Превышен лимит OOXML: 10000 частей или 100 MiB.')
        if len({item.filename for item in entries}) != len(entries):
            raise ValueError('Повторяющиеся имена частей OOXML запрещены.')
        documents = {}
        for item in entries:
            if item.file_size > MAX_ENTRY or item.flag_bits & 1:
                raise ValueError('Часть OOXML превышает 10 MiB или зашифрована.')
            if item.filename.endswith(('.xml', '.rels')):
                raw = archive.read(item)
                # Decode first so UTF-16 declarations cannot bypass the DTD check.
                encoding = 'utf-8-sig'
                if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
                    encoding = 'utf-16'
                elif raw[:2] == b'<\x00':
                    encoding = 'utf-16-le'
                elif raw[:2] == b'\x00<':
                    encoding = 'utf-16-be'
                scan = raw.decode(encoding)
                if '\x00' in scan:
                    raise ValueError('NUL в XML или неподдерживаемая кодировка OOXML.')
                if re.search(r'<!\s*(DOCTYPE|ENTITY)', scan, re.I):
                    raise ValueError('DTD и ENTITY запрещены в OOXML.')
                documents[item.filename] = ET.fromstring(raw)

        warnings = []

        def relationships(owner):
            relpath = posixpath.join(posixpath.dirname(owner), '_rels', posixpath.basename(owner) + '.rels')
            result = {}
            root = documents.get(relpath)
            if root is not None:
                for relation in root:
                    if relation.get('TargetMode') == 'External':
                        warnings.append('Внешняя связь пропущена: ' + relation.get('Id', ''))
                        continue
                    result[relation.get('Id')] = resolve_part(owner, relation.get('Target', ''))
            return result

        workbook = documents.get('xl/workbook.xml')
        if workbook is None or workbook.find('m:sheets', NS) is None:
            raise ValueError('Не найден стандартный xl/workbook.xml с листами.')
        shared_root = documents.get('xl/sharedStrings.xml')
        shared = [all_text(item) for item in shared_root] if shared_root is not None else []
        styles = documents.get('xl/styles.xml')

        def style_list(name):
            parent = styles.find('m:' + name, NS) if styles is not None else None
            return list(parent) if parent is not None else []

        fills, borders, formats = style_list('fills'), style_list('borders'), style_list('cellXfs')

        def cell_style(index):
            if index < 0 or index >= len(formats):
                return {}
            style = dict(formats[index].attrib)
            for key, source, label in [('fillId', fills, 'fill'), ('borderId', borders, 'border')]:
                number = int(style.get(key, '0'))
                if 0 <= number < len(source):
                    style[label] = tree_data(source[number])
            return style

        output = {'schemaVersion': 1, 'status': 'STRUCTURE_ONLY', 'formulasEvaluated': False,
                  'sqlExecuted': False, 'visionStatus': 'NOT_TESTED', 'sheets': [], 'warnings': warnings}
        book_rels = relationships('xl/workbook.xml')
        for definition in workbook.find('m:sheets', NS):
            part = book_rels.get(definition.get('{' + REL + '}id'))
            if part not in documents:
                raise ValueError('Не найдена внутренняя часть листа: ' + definition.get('name', ''))
            root = documents[part]
            sheet = {'name': definition.get('name'), 'state': definition.get('state', 'visible'),
                     'cells': [], 'rows': [], 'columns': [], 'mergedRanges': [], 'tables': [],
                     'inferredBlocks': [], 'fieldCandidates': [], 'headingCandidates': [], 'sqlHints': []}
            columns = root.find('m:cols', NS)
            if columns is not None:
                sheet['columns'] = [dict(col.attrib) for col in columns]
            row_numbers = set()
            for row in root.findall('m:sheetData/m:row', NS):
                sheet['rows'].append(dict(row.attrib))
                for cell in row.findall('m:c', NS):
                    address, kind = cell.get('r', ''), cell.get('t', 'n')
                    if not re.fullmatch(r'[A-Z]{1,3}[1-9][0-9]*', address):
                        raise ValueError('Некорректный адрес ячейки.')
                    value = cell.findtext('m:v', default='', namespaces=NS)
                    if kind == 's':
                        number = int(value)
                        if not 0 <= number < len(shared):
                            raise ValueError('Некорректный индекс sharedStrings.')
                        value = shared[number]
                    elif kind == 'inlineStr':
                        value = all_text(cell.find('m:is', NS))
                    formula = cell.findtext('m:f', default=None, namespaces=NS)
                    sheet['cells'].append({'address': address, 'type': kind, 'value': value,
                                           'formula': formula, 'style': cell_style(int(cell.get('s', '0')))})
                    row_numbers.add(int(re.search(r'[0-9]+', address).group()))
                    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', value):
                        sheet['fieldCandidates'].append({'address': address, 'candidate': value,
                                                         'status': 'UNVERIFIED', 'reason': 'Нужна сверка с исходной моделью.'})
                    if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|EXECUTE|CREATE|DROP)\b', value, re.I):
                        sheet['sqlHints'].append({'address': address, 'status': 'TEXT_ONLY_NOT_EXECUTED'})
            sheet['mergedRanges'] = [item.get('ref') for item in root.findall('m:mergeCells/m:mergeCell', NS)]
            values = {item['address']: item['value'] for item in sheet['cells']}
            for merged in sheet['mergedRanges']:
                sheet['headingCandidates'].append({'range': merged, 'value': values.get(merged.split(':')[0], ''), 'status': 'UNVERIFIED'})
            sheet_rels = relationships(part)
            for table in root.findall('m:tableParts/m:tablePart', NS):
                target = sheet_rels.get(table.get('{' + REL + '}id'))
                if target not in documents:
                    raise ValueError('Не найдена внутренняя часть таблицы.')
                sheet['tables'].append(dict(documents[target].attrib))
            # Row-contiguous regions are candidates, not inferred business tables.
            blocks = []
            for number in sorted(row_numbers):
                if blocks and number == blocks[-1][-1] + 1:
                    blocks[-1].append(number)
                else:
                    blocks.append([number])
            sheet['inferredBlocks'] = [{'firstRow': block[0], 'lastRow': block[-1], 'status': 'UNVERIFIED'} for block in blocks]
            output['sheets'].append(sheet)
        return output


def export(source, output):
    result = parse_workbook(source)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    markdown = ['# Структурный XLSX-макет', '', 'Формулы и SQL не исполнялись. Сопоставления UNVERIFIED; vision NOT_TESTED.', '']
    for sheet in result['sheets']:
        markdown += ['## ' + sheet['name'].replace('\n', ' '), '', 'Merged ranges: ' + ', '.join(sheet['mergedRanges']), '', '| Ячейка | Значение | Формула (не вычисляется) |', '|---|---|---|']
        for cell in sheet['cells']:
            values = [cell['address'], cell['value'], cell['formula'] or '']
            markdown.append('| ' + ' | '.join(str(value).replace('|', '\\|').replace('\n', '<br>') for value in values) + ' |')
        markdown += ['', 'Подробные styles, borders, fills, outline, tables и кандидаты полей: mockup.json.', '']
    for name, content in [('mockup.json', json.dumps(result, ensure_ascii=False, indent=2)), ('mockup.md', '\n'.join(markdown))]:
        destination = output / name
        temporary = output / (name + '.tmp')
        temporary.write_text(content, encoding='utf-8')
        temporary.replace(destination)
    return result


def main():
    parser = argparse.ArgumentParser(description='Офлайн структура XLSX, без SQL, Excel и моделей.')
    parser.add_argument('source', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = export(args.source, args.out)
        print('PASS: листов ' + str(len(result['sheets'])) + '; SQL/model calls=0')
        return 0
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        print('Ошибка разбора XLSX: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
