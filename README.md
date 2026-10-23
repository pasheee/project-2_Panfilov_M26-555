# Primitive DB

Учебная консольная база данных: создание таблиц, CRUD-операции,
хранение в JSON и вывод записей через PrettyTable.

## Установка и запуск

Нужны Python 3.12 или новее и `uv`.

Запуск из исходников:

```bash
uv sync
uv run database
```

Установка собранного пакета как отдельного CLI-инструмента:

```bash
uv build
uvx twine check dist/*
uv tool install --reinstall dist/*.whl
database
```

Если команда `database` не найдена, выполните `uv tool update-shell`
и перезапустите терминал. Проверка `twine check` не публикует пакет на PyPI.

## Команды

Поддерживаются типы `int`, `str`, `bool`. Столбец `ID:int` добавляется
автоматически в начало схемы. Первый ID — `0`.

```text
create_table <таблица> <столбец:тип> ...
list_tables
drop_table <таблица>
insert into <таблица> values (<значение>, ...)
select from <таблица>
select from <таблица> where <столбец> = <значение>
update <таблица> set <столбец> = <значение> where <столбец> = <значение>
delete from <таблица> where <столбец> = <значение>
info <таблица>
help
exit
```

Строки заключайте в двойные кавычки, логические значения записывайте
как `true` и `false`. В условиях ставьте пробелы вокруг `=`.
Одна команда поддерживает одно условие `where` и одно присваивание `set`.

## Декораторы и кэш

- `handle_db_errors` выводит сообщение об ошибке и позволяет ввести следующую
  команду. Сохранение запускается только после успешной операции.
- `confirm_action` запрашивает подтверждение перед `delete` и `drop_table`.
  Введите `y` для выполнения или `n` для отмены и нажмите Enter.
  Введённый ответ скрыт. При отмене файлы не изменяются.
- `log_time` показывает время выполнения успешных `insert`, `select`, `update`
  и `delete` через `time.perf_counter()`. Ожидание подтверждения в замер не входит.
- `create_cacher` хранит результаты одинаковых `select` в замыкании.
  Ключ состоит из имени таблицы и неизменяемого условия `frozendict`.
  После успешного изменения данных или схемы очищается только кэш затронутой
  таблицы. Кэш других таблиц сохраняется; при выходе из программы весь кэш исчезает.

Ctrl+C и Ctrl+D завершают программу без traceback.

## Пример работы

```sql
create_table users name:str age:int is_active:bool
insert into users values ("Sergei", 28, true)
select from users where age = 28
update users set age = 29 where name = "Sergei"
select from users where age = 29
delete from users where ID = 0
info users
drop_table users
exit
```

Удаление строки и таблицы потребует подтверждения. После `n` операция отменяется,
после `y` выполняется. Неверный тип, неизвестный столбец или отсутствующая таблица
вызывают сообщение об ошибке, после которого можно продолжить работу.

Схемы хранятся в `meta.json`, данные таблиц — в `data/<таблица>.json`
рядом с модулем `constants.py`, независимо от текущей папки терминала.
При установке через `uv tool` эти файлы находятся внутри установленного пакета.
`drop_table` удаляет описание таблицы из метаданных; её JSON-файл пока сохраняется.

## Проверки

```bash
uv run ruff check .
uv run python -m unittest discover -s tests -v
uv build
uvx twine check dist/*
```

## Финальная демонстрация

Запись показывает CRUD, повторные выборки, обработку неверного ввода,
замер времени и отмену/подтверждение удаления строк и таблицы.

[![asciicast](https://asciinema.org/a/FVybE6Wvl2XSXc1x.svg)](https://asciinema.org/a/FVybE6Wvl2XSXc1x)

[Локальная копия записи](docs/database-final.cast):

```bash
uvx asciinema play docs/database-final.cast
```
