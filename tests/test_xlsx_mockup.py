import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'xlsx_mockup.py'


def fixture(path, external=False):
    entries = {
        'xl/workbook.xml': '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Макет" sheetId="1" r:id="rId1"/></sheets></workbook>''',
        'xl/_rels/workbook.xml.rels': '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/></Relationships>''',
        'xl/sharedStrings.xml': '''<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Заголовок</t></si><si><r><t>По</t></r><r><t>ле</t></r></si></sst>''',
        'xl/styles.xml': '''<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fills><fill><patternFill patternType="solid"><fgColor rgb="FFABCDEF"/></patternFill></fill></fills><borders><border><bottom style="thin"/></border></borders><cellXfs><xf fillId="0" borderId="0" numFmtId="0"/></cellXfs></styleSheet>''',
        'xl/worksheets/sheet1.xml': '''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><cols><col min="1" max="2" width="15" outlineLevel="1"/></cols><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c></row><row r="2" outlineLevel="1"><c r="A2" t="inlineStr"><is><t>field_id</t></is></c><c r="B2" t="s"><v>1</v></c><c r="C2"><f>1+1</f><v>2</v></c></row><row r="3"><c r="A3" t="inlineStr"><is><t>SELECT confidential FROM synthetic</t></is></c></row></sheetData><mergeCells><mergeCell ref="A1:B1"/></mergeCells><tableParts><tablePart r:id="t1"/></tableParts></worksheet>''',
        'xl/worksheets/_rels/sheet1.xml.rels': '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="t1" Target="../tables/table1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/table"/></Relationships>''',
        'xl/tables/table1.xml': '''<table xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" name="SyntheticTable" ref="A2:C3"/>''',
    }
    if external:
        part = 'xl/worksheets/_rels/sheet1.xml.rels'
        entries[part] = entries[part].replace('</Relationships>', '<Relationship Id="external" Target="https://example.invalid/never" TargetMode="External" Type="hyperlink"/></Relationships>')
    with zipfile.ZipFile(path, 'w') as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


class XlsxMockupTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location('xlsx_mockup', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_structure_styles_and_uncertain_mapping(self):
        with tempfile.TemporaryDirectory(prefix='макет с пробелом ') as folder:
            source = Path(folder) / 'fixture.xlsx'
            fixture(source)
            result = self.load_module().parse_workbook(source)
            sheet = result['sheets'][0]
            self.assertEqual(sheet['name'], 'Макет')
            self.assertEqual(sheet['mergedRanges'], ['A1:B1'])
            cells = {cell['address']: cell for cell in sheet['cells']}
            self.assertEqual(cells['B2']['value'], 'Поле')
            self.assertEqual(cells['C2']['formula'], '1+1')
            self.assertEqual(cells['C2']['value'], '2')
            self.assertEqual(cells['A2']['style']['fill']['patternFill']['fgColor']['rgb'], 'FFABCDEF')
            self.assertEqual(sheet['rows'][1]['outlineLevel'], '1')
            self.assertEqual(sheet['columns'][0]['outlineLevel'], '1')
            self.assertEqual(sheet['tables'][0]['ref'], 'A2:C3')
            self.assertTrue(any(item['candidate'] == 'field_id' and item['status'] == 'UNVERIFIED' for item in sheet['fieldCandidates']))
            self.assertTrue(any(item['address'] == 'A3' for item in sheet['sqlHints']))

    def test_writes_json_and_markdown_without_evaluation(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'fixture.xlsx'
            fixture(source)
            module = self.load_module()
            module.export(source, Path(folder) / 'out')
            parsed = json.loads((Path(folder) / 'out/mockup.json').read_text(encoding='utf-8'))
            self.assertEqual(parsed['formulasEvaluated'], False)
            self.assertEqual(parsed['sqlExecuted'], False)
            self.assertIn('A1:B1', (Path(folder) / 'out/mockup.md').read_text(encoding='utf-8'))

    def test_rejects_external_relationships_and_dtd(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'fixture.xlsx'
            for encoding in ('utf-8', 'utf-16', 'utf-16-le', 'utf-32'):
                with self.subTest(encoding=encoding):
                    fixture(source)
                    payload = ' \n<!DOCTYPE x [<!ENTITY x "unsafe">]><x>&x;</x>'.encode(encoding)
                    with zipfile.ZipFile(source, 'a') as archive:
                        archive.writestr('xl/unused.xml', payload)
                    with self.assertRaisesRegex(ValueError, 'DTD|NUL'):
                        self.load_module().parse_workbook(source)


if __name__ == '__main__':
    unittest.main()
