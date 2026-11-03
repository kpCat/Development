# Development

Переносимая офлайн-обвязка для проектного coding-агента. Текущий режим — **PREP ONLY**: Skills, документация, resolver, статические проверки и структурный XLSX parser. Локальные модели и службы не запускаются. Целевой контекст **65536 токенов, FUTURE_NOT_TESTED**.

Требования: Windows PowerShell 5.1 и Python 3.8+ в PATH. Сторонние Python-пакеты, UAC и администратор не нужны. Используйте доверенный checkout; скрипты сначала просмотрите.

1. Один раз зарегистрируйте проект из корня Development: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Set-Project.ps1 -Name mkr -PickFolder`. Вместо picker можно передать `-Path` с текущим абсолютным путём. Запись попадёт только в ignored `config/projects.local.json`.
2. Проверьте `scripts/Get-Project.ps1 -Name mkr`, затем `scripts/doctor.ps1 -Name mkr`. Корень должен содержать `.git`, решение и исходники; недоступный путь требует повторной регистрации.
3. Выполните `scripts/start-mkr.ps1 -DryRun`. План содержит рабочую папку, отдельный argument-массив, статус PREPARED_UNTESTED и будущий размер контекста. По умолчанию вызов без флагов тоже только DryRun.
4. Читайте проектные `AGENTS.md`, `docs/ai/INDEX.md` и 1–3 подходящих `.agents/skills/*/SKILL.md`. Детальные guides/recipes открывайте по необходимости.

Из произвольной текущей папки вызывайте скрипт через его полный путь; зависимости он находит относительно собственного расположения. Приоритет resolver: явный `-ProjectRoot`, переменная `MKR_PROJECT_ROOT`/`MKP_PROJECT_ROOT`, локальный JSON. После переноса повторите Set-Project; сами Skills используют относительные anchors. Публичный [пример конфигурации](config/projects.example.json) содержит пустые roots и выключенный будущий provider URL. Этот URL скрипты не опрашивают.

Для MKP выполните отдельную регистрацию `-Name mkp` и используйте `scripts/start-mkp.ps1 -DryRun`. MKR нельзя зарегистрировать под MKP; проектные знания не копируются между профилями. Реальный MKP в рамках R2 не исследован.

Для будущего Bionic: Create Project → Allow coding → Choose folder → корень ASU-MKR → Create. Каждая следующая задача — отдельная Session того же Project. После переноса выберите Change working directory в параметрах рабочей папки. Это документированный GUI-путь; `start-mkr.ps1 -Harness bionic` выводит инструкцию без открытия приложения. [Создание проекта](https://lmstudio.ai/docs/bionic/quick-start), [смена рабочей папки](https://lmstudio.ai/docs/bionic/agent/code-project), [Projects/Sessions](https://lmstudio.ai/docs/bionic/projects-and-sessions).

Skills подключаются через Settings → Skills; проверьте Use skills found in other apps и доступность нужных навыков через `@`. Автообнаружение конкретной установленной версией здесь не проверялось. Единый источник — проектная `.agents/skills`, дополнительных копий не создаём. [Официальная инструкция Skills](https://lmstudio.ai/docs/bionic/agent/skills).

Для будущего OpenCode подготовлен [V2 config](config/opencode.example.json). Установленного OpenCode в PATH при подготовке не обнаружено: **PREPARED_UNTESTED**. После отдельного решения о первом запуске сверить установленную major version и конфигурацию; V1 и V2 различаются. Только явный `scripts/start-mkr.ps1 -Launch` исполняет `opencode` с cwd и аргументом корня. OpenCode может автоматически запустить собственный background server — поэтому сейчас даже открытие TUI не проверялось. [CLI](https://opencode.ai/v2/docs/cli/).

Обычный chat LM Studio сам по себе не предоставляет агенту файловые и shell-инструменты репозитория. Их предоставляет coding harness; provider/model и параметры runtime настраиваются отдельно позже. Подробные [профили и ограничения](docs/HARNESSES.md), [перенос и безопасность](docs/PORTABILITY.md), [XLSX pipeline](docs/XLSX.md).

Офлайн-проверки из корня:

```powershell
python -m unittest discover -s tests -p "test_*.py"
powershell -NoProfile -ExecutionPolicy Bypass -File tests/test-resolver.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tests/check-powershell.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-skill-library.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/safety-audit.ps1
```

Последний скрипт проверяет публикуемый working allowlist. `-Staged` отдельно читает индекс Git только по явному запросу; пустой индекс выводит EMPTY_INDEX. Перед любым будущим commit необходим ручной diff/content review. Приватные совпадения можно задать через `-PrivatePatternsPath` с ignored локальным JSON-массивом regex. Ни scanner, ни `.gitignore` не доказывают отсутствие всех утечек.

Итог R2: [RESULT.md](docs/tasks/DEVELOPMENT-HARNESS-001-R2/RESULT.md). Ручная приёмка обязательна; успешные статические проверки не подтверждают способность модели пользоваться Skills.
