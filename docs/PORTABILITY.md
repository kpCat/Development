# Регистрация и перенос

Set-Project нормализует только предоставленный существующий абсолютный путь, проверяет markers и атомарно обновляет local JSON. Разрешено чтение `.git`-файла worktree вместо каталога. Имя папки само по себе ничего не доказывает. MKP требует собственное решение и src, фактический стек в R2 не исследуется.

`-ConfigPath` предназначен для изолированного теста/локальной конфигурации. Если он используется в работе, держите файл вне public candidate set. Рабочий default — `config/projects.local.json`, он ignored. Других постоянных хранилищ paths нет. Тесты создают только искусственные roots в TEMP и не подменяют реальную регистрацию.

При перемещении обновите Set-Project или env один раз. Source-relative anchors не меняются. Пропавший root выдаёт ошибку; fallback на прежний диск и поиск по дискам отсутствуют. Ссылки в приватных документах явно определены относительно корня проекта; это договор библиотеки, который будущий агент должен соблюдать.

doctor читает filesystem и Get-Command metadata. Он не вызывает binaries, package managers, health endpoints или DB. NOT_FOUND у OpenCode/Bionic означает только отсутствие команды в PATH. Наличие dotnet не доказывает пригодность toolchain и лицензий.

По умолчанию safety-audit сканирует README, AGENTS, .gitignore, config, scripts, tests, docs; ignored local JSON и Python cache исключены. Это публичный working allowlist, не весь диск. `-Staged` дополнительно читает точные bytes staged additions/modifications/renames через `git diff --cached` и `git show :path`, не меняя индекс. Private deny patterns храните только локально; совпадения выводятся как filename/reason, без payload.

Файлы PS с кириллицей — UTF-8 BOM для 5.1; JSON/Markdown/Python — UTF-8. ExecutionPolicy Bypass в примерах относится к одному процессу доверенного проверенного скрипта; постоянная политика не меняется. Локальный путь может появляться в выводе resolver/DryRun — такой вывод не публикуйте.
