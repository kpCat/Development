# Структурный XLSX pipeline

`scripts/export-xlsx-mockup.ps1 -Path <workbook> -OutputDirectory <локальный-каталог>` вызывает Python standard-library parser. Путь с пробелами передавайте как один quoted argument. Реальные workbook и output держите в ignored outputs либо вне публичного repo.

Результаты: `mockup.json` со sheets, cell addresses/raw values, formula text/cache, shared/inline strings, merge ranges, row/column outline и attributes, styles fills/borders, formal table names/ranges, contiguous-row blocks. `mockup.md` — читаемая таблица ячеек. Содержимое workbook приватно, включая SQL hints; результаты не публиковать автоматически.

Field IDs определяются как текстовые кандидаты, заголовки — по merged ranges. Каждое сопоставление UNVERIFIED; цвет/граница/английское имя не доказывает связь с доменным полем. Блоки без formal table — эвристика по смежным строкам. Сверку с моделью/SQL делает человек/будущий агент в разрешённом private workspace. SQL остаётся текстом.

Ограничения: поддержан обычный transitional OOXML, без Excel COM, OCR, formulas evaluation, macro execution, DB и сети. Числа/даты сохраняются raw с numFmtId; форматированное отображение Excel не воспроизводится. Внешние связи пропускаются с warning; DTD/entities, encrypted ZIP и выход из package path отвергаются. Лимиты: 10000 частей, 10 MiB на часть, 100 MiB суммарно. Обрабатывается содержимое ZIP в памяти без извлечения на диск. JSON и Markdown заменяются атомарно по отдельности; общей транзакции двух файлов нет.

Искусственные fixtures генерируются в tests и TEMP. Наличие пользовательского workbook не предполагается, он не использовался. Будущий pipeline: XLSX structure → проверенные source mappings → дизайн; screenshot → отдельная vision-гипотеза → сравнение с XLSX. Vision **NOT_TESTED**, модели сейчас не запускаются.
