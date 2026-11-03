import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StaticChecksTests(unittest.TestCase):
    def test_public_safety_rejects_paths_secrets_and_private_files(self):
        audit = load('safety_audit')
        self.assertEqual(audit.scan('config/projects.example.json', b'{"root":""}', []), [])
        self.assertEqual(audit.scan('config/public.json', b'{"url":"https://example.invalid"}', []), [])
        self.assertEqual(audit.scan('scripts/marker.ps1', b'src/libs/MKR.Core', []), [])
        for layer in ('libs', 'modules', 'services'):
            private_anchor = ('[method](src/' + layer + '/MKR.' + 'Core/Private/Example.cs#Read)').encode()
            self.assertTrue(audit.scan('docs/private.md', private_anchor, []))
        absolute = ('C' + ':/' + 'personal/project').encode()
        self.assertTrue(audit.scan('config/public.json', absolute, []))
        unc = (chr(92) * 2 + 'server' + chr(92) + 'share').encode()
        self.assertTrue(audit.scan('config/public.json', unc, []))
        unix = ('/' + 'home' + '/' + 'personal' + '/project').encode()
        self.assertTrue(audit.scan('config/public.json', unix, []))
        secret = ('pass' + 'word=' + 'synthetic-value').encode()
        self.assertTrue(audit.scan('README.md', secret, []))
        self.assertTrue(audit.scan('.local/private.md', b'text', []))
        self.assertTrue(audit.scan('snapshot.png', b'PNG', []))
        self.assertTrue(audit.scan('notes.md', b'private-pattern', ['private-pattern']))

    def test_skill_checker_rejects_missing_source_symbol(self):
        checker = load('check_library')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            skill = root / '.agents/skills/mkr-fixture/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text('---\nname: mkr-fixture\ndescription: Проверка тестового навыка.\n---\n' +
                             '\n'.join('## Раздел ' + str(i) for i in range(8)) +
                             '\n[missing](src/Absent.cs#Missing)\n', encoding='utf-8')
            result = checker.validate(root, root, minimum=1)
            self.assertTrue(any('Absent.cs' in item for item in result['errors']))
            self.assertEqual(result['status'], 'FAIL')
            source = root / 'src/Present.cs'
            source.parent.mkdir()
            source.write_text('class Existing {}', encoding='utf-8')
            skill.write_text(skill.read_text(encoding='utf-8').replace('Absent.cs', 'Present.cs'), encoding='utf-8')
            result = checker.validate(root, root, minimum=1)
            self.assertTrue(any('символ не найден' in item for item in result['errors']))
            skill.write_text(skill.read_text(encoding='utf-8').replace('description: Проверка', 'description: Сценарий: Проверка'), encoding='utf-8')
            result = checker.validate(root, root, minimum=1)
            self.assertTrue(any('YAML scalar' in item for item in result['errors']))

    def test_xlsx_external_links_are_skipped_without_network(self):
        from test_xlsx_mockup import fixture
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'fixture.xlsx'
            fixture(source, external=True)
            result = load('xlsx_mockup').parse_workbook(source)
            self.assertFalse(result['sqlExecuted'])
            self.assertFalse(result['formulasEvaluated'])
            self.assertTrue(any('external' in warning for warning in result['warnings']))


if __name__ == '__main__':
    unittest.main()
