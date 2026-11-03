"""Public content/staged audit. Read-only git only when --staged is explicit."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

TEXT_SUFFIXES = {'.md','.ps1','.py','.json','.jsonc','.txt','.yml','.yaml','.example'}
DENIED_SUFFIXES = {'.png','.jpg','.jpeg','.gif','.xlsx','.xlsm','.docx','.pdf','.zip','.fdb','.gdb','.gguf','.safetensors','.dll','.exe','.pfx','.key'}
ABSOLUTE = re.compile(r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|(?<!\\)\\\\(?!\\)[A-Za-z0-9_.-]+\\[A-Za-z0-9_$ .-]+|/(?:Users|home)/[A-Za-z0-9_.-]+/)')
SECRET = re.compile(r'''(?ix)(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)\s*["']?\s*[:=]\s*["']?([a-z0-9_./+\-]{6,})''')
PRIVATE = re.compile(r'namespace\s+MKR\.|src/(?:libs|modules|services)/(?:MKR\.[A-Za-z0-9_.-]+/|Shared/)|src/MKR\.[A-Za-z0-9_.-]+/|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY')


def scan(name, raw, extra_patterns):
    errors = []
    path = PurePosixPath(name.replace('\\', '/'))
    if any(part in {'.local','.codex-tasks','.git','__pycache__','node_modules','outputs','logs','artifacts'} for part in path.parts):
        errors.append('закрытый/временный путь')
    if path.name.endswith('.local.json') or path.name.startswith('.env') or path.suffix.lower() in DENIED_SUFFIXES:
        errors.append('локальная конфигурация/данные/binary')
    if len(raw) > 2 * 1024 * 1024:
        errors.append('файл больше 2 MiB: нужен отдельный review')
        return errors
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return errors + ['не UTF-8 текст: нужен отдельный review']
    if ABSOLUTE.search(text):
        errors.append('абсолютный локальный путь')
    if SECRET.search(text):
        errors.append('возможный секрет')
    if PRIVATE.search(text):
        errors.append('возможный приватный исходник/anchor')
    if any(re.search(pattern, text, re.I) for pattern in extra_patterns):
        errors.append('локальный private deny pattern')
    return errors


def working_files(root):
    for name in ('README.md','AGENTS.md','.gitignore'):
        path = root / name
        if path.is_file():
            yield path
    for directory in ('config','scripts','tests','docs'):
        for path in sorted((root / directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and not path.name.endswith('.local.json'):
                yield path


def audit(root, staged=False, patterns=None):
    root = Path(root).resolve()
    extra = json.loads(Path(patterns).read_text(encoding='utf-8-sig')) if patterns else []
    if not isinstance(extra, list) or any(not isinstance(item, str) or not item for item in extra):
        raise ValueError('Private patterns должны быть массивом непустых regex-строк.')
    findings, count = [], 0
    if staged:
        # No global safe.directory/config changes and no index mutations.
        result = subprocess.run(['git','-C',str(root),'diff','--cached','--name-only','--diff-filter=ACMR','-z'], check=True, capture_output=True)
        names = [name.decode('utf-8') for name in result.stdout.split(b'\0') if name]
        contents = ((name, subprocess.run(['git','-C',str(root),'show',':' + name], check=True, capture_output=True).stdout) for name in names)
    else:
        contents = ((path.relative_to(root).as_posix(), path.read_bytes()) for path in working_files(root))
    for name, raw in contents:
        count += 1
        issues = scan(name, raw, extra)
        if issues:
            # Never print matched payloads/secrets.
            findings.append({'file': name, 'issues': issues})
    return {'mode': 'STAGED' if staged else 'WORKING_ALLOWLIST', 'filesChecked': count,
            'status': 'FAIL' if findings else ('EMPTY_INDEX' if staged and not count else 'PASS'),
            'findings': findings, 'manualReviewRequired': True}


def main():
    parser = argparse.ArgumentParser(description='Проверка публичных материалов без раскрытия совпавших секретов.')
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--staged', action='store_true')
    parser.add_argument('--patterns', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.root, args.staged, args.patterns)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['findings'] else 0
    except (OSError, ValueError, re.error, subprocess.CalledProcessError) as error:
        print('Аудит не завершён: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
