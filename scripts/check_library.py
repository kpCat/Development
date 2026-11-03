"""Static project-local skill and source-anchor validation; no agent calls."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ABSOLUTE = re.compile(r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|(?<!\\)\\\\(?!\\)[A-Za-z0-9_.-]+\\[A-Za-z0-9_$ .-]+|/(?:Users|home)/[A-Za-z0-9_.-]+/)')
ESCAPED = re.compile(r'\\u0[45][0-9a-f]{2}|&#[xX]0[45][0-9a-f]{2};', re.I)
MOJIBAKE = ('Рџ','Рќ','Рћ','Р•','РЎ','Р›','Р¤','Рњ','РЈ','Рљ','Рґ','Рµ','Р°','Р»','РЅ','Рѕ','СЏ','С€','СЂ','С‹','СЊ','С‚','Сѓ','С‡','С…','С†','�')
CORE = {'mkr-git-safety','mkr-targeted-tests','mkr-build-net48','mkr-ui-localization',
        'mkr-dependent-selector','mkr-grid-bands','mkr-grid-lookup','mkr-mvvm',
        'mkr-repository-query','mkr-code-style'}


def scalar(value):
    """Validate the intentionally narrow YAML subset used by this library."""
    value = value.strip()
    if value.startswith('"'):
        decoded = json.loads(value)  # JSON quoted strings are valid YAML scalars.
        if not isinstance(decoded, str):
            raise ValueError('нужна строка')
        return decoded
    if value.startswith("'"):
        if not value.endswith("'") or re.search(r"(?<!')'(?!')", value[1:-1]):
            raise ValueError('неверная single-quoted строка')
        return value[1:-1].replace("''", "'")
    if not value or value[0] in '{}[]!&*|>%@`' or ': ' in value or ' #' in value:
        raise ValueError('scalar требует корректного YAML quoting')
    return value


def validate(project, library, minimum=32):
    errors, warnings = [], []
    project, library = Path(project).resolve(), Path(library).resolve()
    skills = sorted((library / '.agents/skills').glob('mkr-*/SKILL.md'))
    ids, evidence_rows, anchor_count = set(), {}, 0
    unique_anchors = set()

    def contained(root, path):
        try:
            path.resolve().relative_to(root)
            return True
        except ValueError:
            return False

    def target(path):
        candidate = library / path
        if not contained(library, candidate):
            return None
        if candidate.is_file():
            return candidate
        candidate = project / path
        return candidate if contained(project, candidate) and candidate.is_file() else None

    def check_anchor(path, symbol, owner):
        nonlocal anchor_count
        file = target(unquote(path))
        if file is None:
            errors.append(owner + ': отсутствует anchor ' + path)
            return
        anchor_count += 1
        unique_anchors.add((path, symbol))
        if symbol and file.suffix.lower() not in ('.md', '.json'):
            value = file.read_text(encoding='utf-8-sig')
            # Fragments are exact source tokens, not line numbers or invented API paths.
            if unquote(symbol) not in value:
                errors.append(owner + ': символ не найден ' + path + '#' + symbol)

    for path in (library / 'docs/ai/evidence').glob('*.json'):
        try:
            rows = json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(rows, list):
                continue
            for row in rows:
                if row.get('id') in evidence_rows:
                    errors.append('Повторный evidence ID: ' + row['id'])
                evidence_rows[row['id']] = row
        except (ValueError, KeyError) as error:
            errors.append(path.name + ': некорректный evidence: ' + str(error))

    for path in skills:
        text = path.read_text(encoding='utf-8-sig')
        match = re.match(r'\A---\r?\n(.*?)\r?\n---\r?\n', text, re.S)
        owner = path.parent.name
        if not match:
            errors.append(owner + ': отсутствует frontmatter')
            continue
        fields = {}
        for line in match.group(1).splitlines():
            pair = re.fullmatch(r'(name|description):\s*(.+)', line)
            if not pair or pair.group(1) in fields:
                errors.append(owner + ': нужны уникальные scalar name/description')
                continue
            try:
                fields[pair.group(1)] = scalar(pair.group(2))
            except ValueError as error:
                errors.append(owner + ': неверный YAML scalar: ' + str(error))
        name, description = fields.get('name', ''), fields.get('description', '')
        if name != owner or len(name) > 64 or not re.fullmatch(r'mkr-[a-z0-9]+(?:-[a-z0-9]+)*', name):
            errors.append(owner + ': неверное имя')
        if not 1 <= len(description) <= 1024 or not re.search('[А-Яа-яЁёІіЇїЄє]', description):
            errors.append(owner + ': требуется русское конкретное description')
        if name in ids:
            errors.append(owner + ': повторный ID')
        ids.add(name)
        body = text[match.end():]
        if len(re.findall(r'^## ', body, re.M)) < 8:
            errors.append(owner + ': менее восьми разделов')
        algorithm = re.search(r'^## [^\n]*Алгоритм[^\n]*\n(.*?)(?=^## |\Z)', body, re.M | re.S | re.I)
        steps = len(re.findall(r'^\d+\. ', algorithm.group(1), re.M)) if algorithm else 0
        if not 5 <= steps <= 10:
            errors.append(owner + ': нужно 5–10 шагов алгоритма')
        if re.search(r'\b(TODO|TBD|YOUR_PATH_HERE)\b', body):
            errors.append(owner + ': незаполненный шаблон')
        row = evidence_rows.get(owner)
        if not row or row.get('status', 'READY_STATIC') != 'READY_STATIC':
            errors.append(owner + ': нет READY_STATIC evidence')
            continue
        anchors = row.get('anchors', [])
        if not 2 <= len(anchors) <= 6:
            errors.append(owner + ': нужны 2–6 evidence anchors')
        for anchor in anchors:
            check_anchor(anchor['path'], anchor.get('symbol', ''), owner)
        scenarios = row.get('scenarios', [])
        if len(scenarios) != 3 or any(not all(item.get(key) for key in ('request','answer','evidence')) for item in scenarios):
            errors.append(owner + ': нужны три доказательных статических сценария')
        for scenario in scenarios:
            reference = scenario.get('evidence', '')
            references = reference if isinstance(reference, list) else reference.split('; ')
            for item in references:
                if isinstance(item, dict):
                    check_anchor(item['path'], item.get('symbol',''), owner + ': scenario')
                elif isinstance(item, str) and re.match(r'(?:src/|tests/|docs/|Directory\.)', item):
                    path_part, _, fragment = item.partition('#')
                    check_anchor(path_part, fragment, owner + ': scenario')
        if not row.get('recipe') or target(row.get('recipe', '')) is None:
            errors.append(owner + ': отсутствует recipe')

    markdown_files = skills + sorted((library / 'docs/ai').rglob('*.md'))
    for path in markdown_files:
        text = path.read_text(encoding='utf-8-sig')
        owner = str(path.relative_to(library))
        if ABSOLUTE.search(text):
            errors.append(owner + ': абсолютный локальный путь')
        if ESCAPED.search(text):
            errors.append(owner + ': escaped Cyrillic')
        hits = [item for item in MOJIBAKE if item in text]
        if hits:
            errors.append(owner + ': mojibake-маркер (требует просмотра)')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if link.startswith(('https://','http://','mailto:','#')):
                continue
            path_part, _, fragment = link.partition('#')
            check_anchor(path_part, fragment, owner)
    coverage = library / 'docs/ai/SKILL_COVERAGE.md'
    if not coverage.is_file():
        errors.append('Отсутствует SKILL_COVERAGE.md')
    else:
        content = coverage.read_text(encoding='utf-8-sig')
        for name in ids:
            lines = [line for line in content.splitlines() if name in line and line.startswith('|')]
            if not any('READY_STATIC' in line for line in lines):
                errors.append(name + ': нет READY_STATIC строки coverage')
    if len(ids) < minimum:
        errors.append('Недостаточно skills: ' + str(len(ids)))
    if minimum >= 32 and CORE - ids:
        errors.append('Отсутствуют core skills: ' + ', '.join(sorted(CORE - ids)))
    return {'skills': len(ids), 'anchorsChecked': anchor_count, 'uniqueAnchors': len(unique_anchors), 'markdownFiles': len(markdown_files),
            'errors': errors, 'warnings': warnings, 'status': 'FAIL' if errors else 'READY_STATIC',
            'modelRuns': 0, 'mojibakeCheck': 'FAIL' if any('mojibake' in item for item in errors) else 'PASS',
            'escapedCyrillicCheck': 'FAIL' if any('escaped Cyrillic' in item for item in errors) else 'PASS'}


def main():
    parser = argparse.ArgumentParser(description='Проверка Skills и source-relative anchors без моделей.')
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--library', type=Path)
    parser.add_argument('--minimum', type=int, default=32)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.project, args.library or args.project, args.minimum)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['errors'] else 0
    except (OSError, ValueError, KeyError) as error:
        print('Ошибка статической проверки: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
