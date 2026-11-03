# RESULT — DEVELOPMENT-HARNESS-001-R2

03.11.2026. **PREP ONLY завершён; MANUAL_REVIEW_REQUIRED.** Gate не объявлен пройденным. Следующий этап inference не начинался.

| Результат | Статус / доказательство |
|---|---|
| Project-local Skills | **39 READY_STATIC**, все 10 обязательных core включены |
| Кандидаты без доказанного workflow | **1 UNVERIFIED**: screenshot/vision; SKILL.md не создан |
| Приватные guides / recipes | **11 / 13**, плюс отдельные README-router |
| Статические мини-сценарии | **117 для READY_STATIC**, ещё 3 для фиксации ограничений UNVERIFIED |
| Frontmatter / имена / anchors / coverage | PASS: 1249 проверенных вхождений, 306 уникальных anchors, 71 Markdown-документ |
| Установка приватных материалов | 75 новых файлов и guarded append AGENTS.md; 76 файлов совпадают со staging по SHA-256 |
| Сохранность исходников и исходного состояния | PASS: 3367 прежних source/project/resource/root/index файлов имеют прежние SHA-256; 10 исходных dirty файлов сохранены |
| Public content audit | PASS по working allowlist; private source anchors/credentials/data не обнаружены |
| Staged-content audit | **EMPTY_INDEX**, exit 0, staged files=0; stage/commit не выполнялись |
| Итоговый ручной gate | **REQUIRED**, не PASS |

```text
MODEL_RUNS=0
LM_STUDIO_SERVER_STARTS=0
LIVE_DB_CONTACTS=0
GIT_PUSHES=0
GIT_MERGES=0
ASU_SOURCE_MUTATIONS=0
TARGET_CONTEXT_TOKENS=65536
CONTEXT_STATUS=FUTURE_NOT_TESTED
```

Модели, загрузки/auto-load, LM Studio API/server, Bionic/OpenCode TUI/inference, Firebird/ЕДБО/BDE/Print/SCM не запускались и не опрашивались. Сеть использовалась только для чтения официальной документации оболочек и Agent Skills, как требует этап D.

## Что создано

В Development изменён README.md; добавлены AGENTS.md, .gitignore, два конфигурационных примера, resolver/doctor/DryRun launchers, validators, OOXML parser и focused tests. Все рабочие roots разрешаются через параметр → env → ignored local JSON. Реальный MKR зарегистрирован один раз в config/projects.local.json; пользовательский путь присутствует только в ignored локальной конфигурации и scratch diagnostics. MKP имеет независимый профиль, реальный checkout MKP не исследован и не зарегистрирован.

Публичные исходные файлы поставки:

- `.gitignore`
- `AGENTS.md`
- `README.md`
- `config/opencode.example.json`
- `config/projects.example.json`
- `docs/HARNESSES.md`
- `docs/PORTABILITY.md`
- `docs/XLSX.md`
- `docs/tasks/DEVELOPMENT-HARNESS-001-R2/RESULT.md`
- `scripts/Get-Project.ps1`
- `scripts/Harness.Common.ps1`
- `scripts/Set-Project.ps1`
- `scripts/check-skill-library.ps1`
- `scripts/check_library.py`
- `scripts/doctor.ps1`
- `scripts/export-xlsx-mockup.ps1`
- `scripts/safety-audit.ps1`
- `scripts/safety_audit.py`
- `scripts/start-mkp.ps1`
- `scripts/start-mkr.ps1`
- `scripts/xlsx_mockup.py`
- `tests/check-powershell.ps1`
- `tests/test-resolver.ps1`
- `tests/test_static_checks.py`
- `tests/test_xlsx_mockup.py`

В ASU-MKR создана полноценная библиотека в `.agents/skills` и `docs/ai`; исходный AGENTS.md сохранён как byte prefix и дополнен короткими правилами. **Реальные source anchors, namespaces, SQL/schema и конкретные примеры находятся только в приватных docs/ai/PROJECT_MAP.md, SKILL_COVERAGE.md, AUDIT.md и evidence JSON.** Здесь приведены только IDs, статусы и состав новых документов.

Все 39 Skills имеют 8 обязательных разделов, 5–10 шагов, 2–6 проверенных file/symbol anchors, конкретный эталон, тематические антипаттерны, проверки, stop rule и связанные навыки. Общие правила вынесены в AGENTS/INDEX; нет копий в .opencode/skills или .claude/skills.

## Полный список Skills

Путь каждого готового навыка в ASU-MKR: `.agents/skills/<id>/SKILL.md`. Полные 3 ответа/доказательства и read-list находятся в соответствующем `docs/ai/evidence/<файл>`. Coverage связывает навыки с живыми anchors и рецептами.

| Skill | Статус | Anchors / сценарии | Private evidence |
|---|---|---|---|
| mkr-async-lifecycle | READY_STATIC | 5 / 3 | `ui.json` |
| mkr-build-net48 | READY_STATIC | 5 / 3 | `print.json` |
| mkr-cache-refresh | READY_STATIC | 6 / 3 | `architecture.json` |
| mkr-code-review | READY_STATIC | 6 / 3 | `architecture.json` |
| mkr-code-style | READY_STATIC | 4 / 3 | `architecture.json` |
| mkr-crud-transaction | READY_STATIC | 6 / 3 | `architecture.json` |
| mkr-debug-diagnostics | READY_STATIC | 5 / 3 | `print.json` |
| mkr-dependent-selector | READY_STATIC | 3 / 3 | `ui.json` |
| mkr-domain-model | READY_STATIC | 5 / 3 | `architecture.json` |
| mkr-edbo-bde | READY_STATIC | 4 / 3 | `print.json` |
| mkr-firebird | READY_STATIC | 5 / 3 | `architecture.json` |
| mkr-form-validation | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-git-safety | READY_STATIC | 2 / 3 | `architecture.json` |
| mkr-grid | READY_STATIC | 3 / 3 | `ui.json` |
| mkr-grid-bands | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-grid-columns | READY_STATIC | 3 / 3 | `ui.json` |
| mkr-grid-crud | READY_STATIC | 3 / 3 | `ui.json` |
| mkr-grid-lookup | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-grid-row-state | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-integration-config | READY_STATIC | 5 / 3 | `print.json` |
| mkr-macro-parser | READY_STATIC | 5 / 3 | `print.json` |
| mkr-module-di | READY_STATIC | 6 / 3 | `architecture.json` |
| mkr-mvvm | READY_STATIC | 5 / 3 | `architecture.json` |
| mkr-print-dates | READY_STATIC | 4 / 3 | `print.json` |
| mkr-print-spreadsheet | READY_STATIC | 4 / 3 | `print.json` |
| mkr-print-word | READY_STATIC | 3 / 3 | `print.json` |
| mkr-reactive-state | READY_STATIC | 5 / 3 | `architecture.json` |
| mkr-repo-navigation | READY_STATIC | 4 / 3 | `architecture.json` |
| mkr-repository-query | READY_STATIC | 5 / 3 | `architecture.json` |
| mkr-schedule-print | READY_STATIC | 5 / 3 | `print.json` |
| mkr-screenshot-mockup | UNVERIFIED | 2 / 3 | `print.json` |
| mkr-selector | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-tab-navigation | READY_STATIC | 5 / 3 | `architecture.json` |
| mkr-targeted-tests | READY_STATIC | 6 / 3 | `print.json` |
| mkr-task-triage | READY_STATIC | 3 / 3 | `architecture.json` |
| mkr-ui-localization | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-ui-performance | READY_STATIC | 4 / 3 | `ui.json` |
| mkr-unit-academic-year | READY_STATIC | 6 / 3 | `architecture.json` |
| mkr-wpf-layout | READY_STATIC | 3 / 3 | `ui.json` |
| mkr-xlsx-mockup | READY_STATIC | 4 / 3 | `print.json` |

## Приватные guides, recipes и служебные документы

Все пути ниже относительно ASU-MKR. Это новые документы, без изменения прежних docs/tasks:

- `AGENTS.md`
- `docs/ai/AUDIT.md`
- `docs/ai/INDEX.md`
- `docs/ai/PROJECT_MAP.md`
- `docs/ai/SKILL_COVERAGE.md`
- `docs/ai/evidence/architecture.json`
- `docs/ai/evidence/print-read-list.md`
- `docs/ai/evidence/print.json`
- `docs/ai/evidence/ui-read-list.md`
- `docs/ai/evidence/ui-static-checks.json`
- `docs/ai/evidence/ui.json`
- `docs/ai/guides/README.md`
- `docs/ai/guides/architecture-navigation.md`
- `docs/ai/guides/bands-layout.md`
- `docs/ai/guides/build-tests-diagnostics.md`
- `docs/ai/guides/domain-periods.md`
- `docs/ai/guides/grid-editors.md`
- `docs/ai/guides/integration-boundaries.md`
- `docs/ai/guides/localization-ui.md`
- `docs/ai/guides/printing-macros.md`
- `docs/ai/guides/reactive-mvvm.md`
- `docs/ai/guides/repository-firebird.md`
- `docs/ai/guides/selectors.md`
- `docs/ai/recipes/README.md`
- `docs/ai/recipes/async-cancel.md`
- `docs/ai/recipes/dependent-selector.md`
- `docs/ai/recipes/editable-row.md`
- `docs/ai/recipes/field-crud-localization.md`
- `docs/ai/recipes/firebird-batch.md`
- `docs/ai/recipes/grid-lookup.md`
- `docs/ai/recipes/new-screen-di.md`
- `docs/ai/recipes/runtime-bands.md`
- `docs/ai/recipes/schedule-date-print.md`
- `docs/ai/recipes/targeted-offline-tests.md`
- `docs/ai/recipes/ui-performance-tests.md`
- `docs/ai/recipes/unit-year-validation.md`
- `docs/ai/recipes/word-spreadsheet-macro.md`

## Проверки и фактические exit codes

`PS51` в таблице означает точную команду `powershell -NoProfile -ExecutionPolicy Bypass -File`. Все команды выполнялись из корня Development. Bypass ограничен процессом; system/global policy не менялась. Отдельный PS fixture также выполняет scripts из произвольного cwd.

| Команда | Exit | Результат |
|---|---|---|
| `python -m unittest discover -s tests -p "test_*.py"` | 0 | 6 focused tests, включая DTD UTF8/UTF16/UTF32, external links, source/symbol/YAML negatives и safety negatives |
| `PS51 tests/test-resolver.ps1` | 0 | JSON/env/argument, relocation, Unicode/spaces, arbitrary cwd, DryRun/default/Bionic, invalid flags/markers, doctor и MKP isolation |
| `PS51 tests/check-powershell.ps1` | 0 | 11 PS файлов: AST parsing и UTF-8 BOM; Windows PowerShell 5.1.19041.6456 |
| `PS51 scripts/doctor.ps1 -Name mkr` | 0 | Docs/skills присутствуют; python/powershell/dotnet найдены, binaries не вызывались; msbuild/OpenCode/Bionic в PATH не найдены |
| `PS51 scripts/start-mkr.ps1 -DryRun` | 0 | План команды, cwd зарегистрированного проекта, target 65536; executable не вызван |
| `PS51 scripts/start-mkr.ps1 -Harness bionic -DryRun` | 0 | GUI_ONLY, без неподтверждённого CLI |
| `PS51 scripts/check-skill-library.ps1 -ReportPath .local/installed-library-validation.json` | 0 | Проверена установленная библиотека: 39 skills, 1249 anchors occurrences / 306 unique, errors=0 |
| `PS51 scripts/export-xlsx-mockup.ps1 -Path '.local/макет с пробелом/fixture.xlsx' -OutputDirectory '.local/макет с пробелом/output'` | 0 | mockup.json + mockup.md, 1 synthetic sheet, SQL/model calls=0 |
| `PS51 scripts/safety-audit.ps1 -ReportPath .local/public-audit-working.json` | 0 | Public working allowlist PASS, без matched payload в выводе |
| `PS51 scripts/safety-audit.ps1 -Staged -ReportPath .local/public-audit-staged.json` | 0 | EMPTY_INDEX, проверены точные staged names; staged content отсутствует |
| `python .local/verify_preservation.py --source .local/source-baseline.json --root .local/root-baseline.json --report .local/preservation-after.json` | 0 | 3367 прежних файлов, changed=0 |
| `python .local/final_verify.py` | 0 | Полная оркестрация перечисленных offline gates, manifest equality и две encoding-проверки |

Журналы и машиночитаемые результаты сохранены в ignored `.local/`; они содержат локальные paths и не входят в public поставку. Одноразовый private apply имел DRY_RUN exit 0, затем APPLY exit 0: 75 additions, source mutations=0, AGENTS append only. Перед apply проверены collision allowlist, root containment и исходный hash AGENTS; существующие source/docs файлы не перезаписывались.

- **mojibake-маркеры в изменённых файлах проверены** — 0 повреждённых строк. Единственное техническое исключение scanner — точная строка с сигнатурами MOJIBAKE в check_library.py; это данные detector, не пользовательский текст.
- **escaped Cyrillic в изменённых файлах проверены** — 0 совпадений Unicode/XML escaped Cyrillic. Проверка отдельная от mojibake.

Дополнительный bundled `skill-creator/quick_validate.py` остановился до проверки с exit 1: отсутствует PyYAML (`ModuleNotFoundError: yaml`). Это **NOT_RUN_DEPENDENCY**, пакеты не устанавливались. Используемый библиотекой ограниченный YAML формат из двух scalar-полей полностью проверен собственным offline checker, включая quoting/имена/длины/невалидные значения. Один unquoted colon исправлен до установки.

Независимый static review выявил и проверенно исправил: обход DTD через UTF16LE с whitespace; пропуск private source anchors Core/modules/services аудитом; пропуск смены cache key после insert. Первые два закрыты воспроизводимыми RED→GREEN fixtures, третий — уточнением source-backed инструкции и отдельным counterfactual. Дополнительно исправлены File.Replace на PS5.1 и конфликт case-insensitive переменной doctor; регрессии проходят.

## Git и сохранность

Git-команды **использовались**, поскольку GOAL прямо требует pre/post status/branch/remote/HEAD, staged-content и ignore audit. Выполнены только read-only формы:

```text
git status --short
git branch --show-current
git remote -v
git rev-parse HEAD
git diff --cached --stat
git check-ignore .codex-tasks/DEVELOPMENT-HARNESS-001-R2/GOAL.md .local/knowledge-summary.json config/projects.local.json
git diff --cached --name-only --diff-filter=ACMR -z
```

Последняя команда вызывается safety-audit с `git -C <текущий-public-root>`; её index пуст, поэтому ветка `git show :<staged-path>` в scanner не исполнялась. Для приватного repo те же status/branch/remote/HEAD вызывались с `-C <source-root>` и process-only `-c safe.directory=<source-root>`, затем `git check-ignore -v docs/ai/INDEX.md .agents/skills/mkr-grid/SKILL.md`. Конкретные user directories не включены в этот публичный отчёт. Глобальный Git config не менялся.

Development: branch `master`, HEAD `2b6c36190f1472a362296deb1a57a9393eacbce2`, origin `git@github.com:kpCat/Development.git`; README modified, новые public files untracked, local config/task/scratch ignored. Source: branch `develop`, исходный HEAD сохранён в private AUDIT.md и не менялся; к 10 исходным modified files добавлен только AGENTS.md. Local commits и новые ветки не создавались, push/merge/reset/clean/stash не выполнялись.

**Особенность private inventory:** существующий source .gitignore уже игнорирует `docs/` и `/.agents/`. Поэтому 75 новых документов присутствуют на диске и проходят checker, но не отображаются как untracked в обычном source git status. Эти правила не изменялись, force-add не выполнялся. Человек при review отдельно решает дальнейшее версионирование библиотеки. Перенос существующей рабочей папки сохраняет знания; новый clone сам по себе пока их не содержит.

Исходники C#/XAML, resx/designer, csproj/props/packages, tests и прежние docs/tasks ASU-MKR не изменены. Сохранность подтверждена SHA-256, а не только списком git status. Development `.codex-tasks` сохранён и исключён из public candidate set. Read-first audit нашёл исходный AGENTS и code-map; их старые WinForms/context сведения разобраны в private map. В Development AGENTS/docs до задачи отсутствовали; source docs/ai, global.json, root Directory.Build.targets и code-map/patterns в исходном checkout не найдены.

## NOT_RUN / OPEN ISSUES и следующий шаг

| Область | Статус / граница |
|---|---|
| Local model selection/inference/tool calling/vision | NOT_TESTED, запусков 0 |
| 65536 context, KV-cache, quantization/offload | FUTURE_NOT_TESTED; только policy, не недокументированный runtime key |
| Bionic/OpenCode installed integration | PREPARED_UNTESTED; executable в PATH не найден; GUI install вне PATH не утверждается |
| ASU-MKR build / tests / UI / performance | NOT_RUN; в этой задаче только source/static audit, без production build |
| DB/schema runtime, ЕДБО/BDE/Print/SCM | NOT_RUN, контактов 0 |
| Реальный пользовательский XLSX | Не использован; наличие не предполагается. Проверен synthetic fixture |
| Screenshot model workflow | UNVERIFIED; нет fake SKILL и vision runs |
| Полная гарантия latest-wins в base selector | Не подтверждена; навыки направляют к конкретным guards и отдельной implementation-задаче |
| CLI resx regeneration / installed toolchain | NOT_RUN; подтверждён generator из csproj, UI/designer automation не выдумана |
| Safety audit | Автоматический scanner + ручное чтение текущих public candidates выполнены; это не гарантия всех возможных утечек. Перед будущим commit повторить staged diff/content audit |

Следующее действие пользователя — ручной review приватного INDEX → COVERAGE → 1–3 важных Skills/recipes и публичной обвязки. Затем отдельно разрешить первый runtime этап, проверить фактическую версию оболочки, выбрать модель/provider и подтвердить доступность Skills в Settings/registry. Bionic настраивается через GUI Project/working directory; OpenCode запускается из registered root только с явным -Launch после приёмки. Во время этого R2 такого запуска не было.
