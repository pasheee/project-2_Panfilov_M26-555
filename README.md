# Управление таблицами

## Установка и запуск

```bash
uv build
uv tool install --reinstall dist/*.whl
database
```

Поддерживаемые типы столбцов: `int`, `str`, `bool`.
Столбец `ID:int` добавляется автоматически, если не указан пользователем,
и всегда находится в начале схемы.

## Список команд:

### Общие команды:

* `help` - справочная информация
* `exit` - выход из программы

### Процесс работы с таблицей:

* `create_table <имя_таблицы> <столбец1:тип> ...` - создать таблицу
* `list_tables` - показать список всех таблиц
* `drop_table <имя_таблицы>` - удалить таблицу

## Пример работы

```text
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.

>>>Введите команду: exit
```

## Демонстрация

Запись показывает установку пакета, запуск БД, создание и удаление таблиц,
сохранение данных после перезапуска и обработку некорректного ввода.

[![asciicast](https://asciinema.org/a/ZGQPnnpusrk4Rd9j.svg)](https://asciinema.org/a/ZGQPnnpusrk4Rd9j)

[Локальная копия записи](docs/database.cast). Воспроизведение в терминале:

```bash
uvx asciinema play docs/database.cast
```
