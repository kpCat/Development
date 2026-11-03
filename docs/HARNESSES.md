# Будущие оболочки: PREPARED_UNTESTED

Проверено по официальной документации 03.11.2026. Двоичные OpenCode/Bionic в PATH не найдены; наличие GUI вне PATH не утверждается. Установка, inference и server startup не выполнялись.

## OpenCode V2

`config/opencode.example.json` — ручной шаблон, автоматически в приватный проект не копируется. После review можно использовать его как проектный `opencode.json`/`opencode.jsonc`. В V2 поле называется `permissions` (массив action/resource/effect), shell-action — `shell`. Последнее совпавшее правило имеет приоритет. Shell требует ask, push/merge и внешние каталоги deny. Это конфигурационный guard, а не OS sandbox; сложные команды требуют ручного review. Provider, model ID и ключи умышленно выбираются пользователем позже. [Config](https://opencode.ai/v2/docs/config), [Permissions](https://opencode.ai/v2/docs/permissions).

Из корня проекта `opencode` открывает TUI; directory-argument тоже документирован. Launcher передаёт путь отдельным аргументом, устанавливая cwd; shell-конкатенации и Invoke-Expression нет. Скрипт запускается только с `-Launch`; `-DryRun` и вызов без флагов не вызывают executable. Не используйте `opencode run` во время PREP ONLY. CLI по умолчанию может поднимать shared service. [CLI](https://opencode.ai/v2/docs/cli/).

OpenCode V2 читает AGENTS.md; проектная `.agents/skills` поддерживается как compatibility source. Подробности навыка загружаются по запросу, поэтому общий registry должен оставаться коротким. Шаблон использует только `name` и `description`, совместимые со стандартом. [Instructions](https://opencode.ai/v2/docs/instructions), [Skills discovery](https://opencode.ai/v2/docs/skills), [Agent Skills specification](https://agentskills.io/specification).

## Bionic и LM Studio

GUI-последовательность настройки и подключения Skills приведена в README. Новый Project указывает на реальный корень, Session получает короткую задачу. Если compatible skill не показан, добавьте конкретный SKILL.md через Settings → Skills; не создавайте расходящиеся копии библиотеки. Доступность проекта и Skills в фактическом UI требует ручной проверки после PREP ONLY. [Bionic Skills](https://lmstudio.ai/docs/bionic/agent/skills).

LM Studio classic — источник будущего inference API; Bionic — агент с проектом и инструментами. Наличие модели в обычном чате не подтверждает repository access. Рабочий API/config не менялся; server не запускался.

## Бюджет 65536

Это собственная policy в projects JSON, **FUTURE_NOT_TESTED**, а не неподтверждённый ключ OpenCode/LM Studio. Практическая вместимость зависит от модели, квантовки, KV cache и offload. Auto-load не нужен для статической подготовки.

План бюджета: до 8K на task/AGENTS/INDEX/registry, до 16K на 1–3 Skills и выбранный guide, до 24K на 1–3 source files/результаты поиска; минимум 16K оставить для tools/output/compaction. Это ориентиры, не измерения. Сначала rg по имени/символу, затем узкое чтение; весь каталог и все исходники одновременно не загружать. Реальное соблюдение бюджета локальной моделью NOT_TESTED.
