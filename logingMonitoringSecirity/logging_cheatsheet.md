# Python `logging`: краткая шпаргалка

`logging` записывает сообщения о работе программы. У каждого сообщения есть уровень важности, время, имя логгера и текст.

## 1. Минимальная настройка

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent")

logger.info("Агент запущен")
```

`basicConfig()` настраивает логирование. `getLogger("agent")` создаёт логгер с именем `agent`. Обычно настройку делают один раз при запуске приложения.

## 2. Уровни сообщений

От менее важного к более важному:

| Уровень | Метод | Когда использовать |
|---|---|---|
| `DEBUG` | `logger.debug(...)` | Подробности для отладки |
| `INFO` | `logger.info(...)` | Обычные важные события |
| `WARNING` | `logger.warning(...)` | Что-то неожиданное, но работа продолжается |
| `ERROR` | `logger.error(...)` | Операция не удалась |
| `CRITICAL` | `logger.critical(...)` | Серьёзная ошибка, приложение может остановиться |

Настройка `level=logging.INFO` показывает `INFO` и уровни выше. `DEBUG` при этом скрыт. Для отладки поставь `level=logging.DEBUG`.

## 3. Ключи `basicConfig`

- `level` — минимальный уровень сообщений.
- `format` — шаблон строки лога.
- `datefmt` — формат времени, если нужно настроить его отдельно.
- `filename` — записывать логи в файл.
- `handlers` — задать, куда отправлять логи, например в консоль и файл.

Частые поля `format`:

- `%(asctime)s` — время;
- `%(name)s` — имя логгера;
- `%(levelname)s` — уровень (`INFO`, `ERROR` и т. д.);
- `%(message)s` — текст сообщения.

## 4. Логирование в функции

```python
def agent_step(user_query: str, user_id: str) -> str:
    logger.info("Запрос от user_id=%s", user_id)
    logger.debug("Длина запроса: %d", len(user_query))

    response = "Ответ-заглушка"
    logger.info("Ответ для user_id=%s сгенерирован", user_id)
    return response
```

`logger.info(...)` и другие методы отправляют сообщение в настроенные обработчики. В примере выше сообщение видно в консоли, потому что `basicConfig()` по умолчанию настраивает вывод туда. Логгер не печатает автоматически возвращаемое функцией значение: его возвращают через `return`, а для вывода используют, например, `print()`. Для динамических значений удобно передавать шаблон и значения отдельными аргументами.

## 5. Куда записывать логи

`StreamHandler` пишет в консоль, `FileHandler` — в файл. Их можно подключить к одному логгеру, чтобы каждое сообщение уходило в оба места:

```python
logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

file = logging.FileHandler("app.log", encoding="utf-8")
file.setFormatter(formatter)
logger.addHandler(file)

logger.info("Агент запущен")  # появится в консоли и в app.log
```

### Запись в SQLite

В стандартной библиотеке нет готового обработчика для базы данных. Для небольшого примера можно создать свой обработчик `logging.Handler`:

```python
import logging
import sqlite3

class SQLiteHandler(logging.Handler):
    def __init__(self, database: str):
        super().__init__()
        self.database = database
        with sqlite3.connect(database) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    created REAL,
                    name TEXT,
                    level TEXT,
                    message TEXT
                )
            """)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            with sqlite3.connect(self.database) as connection:
                connection.execute(
                    "INSERT INTO logs VALUES (?, ?, ?, ?)",
                    (record.created, record.name, record.levelname, record.getMessage()),
                )
        except Exception:
            self.handleError(record)

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
logger.addHandler(SQLiteHandler("app.db"))
logger.info("Агент запущен")  # новая строка появится в таблице logs
```

Для настоящего приложения запись в базу обычно делают через очередь или отдельный сервис: открывать соединение на каждое сообщение может быть медленно.

## 6. Логгер и вывод

```python
logger = logging.getLogger("agent")
logger.info("Готово")
```

Имя `agent` попадёт в `%(name)s`. По умолчанию логи выводятся в `stderr`, а `print()` — в `stdout`; среда запуска может показать их в неожиданном порядке.

## Запомнить

`basicConfig()` → общая настройка.  
`getLogger()` → получить логгер.  
`debug/info/warning/error/critical` → записать событие нужной важности.  
`level` → выбрать, какие уровни показывать.  
`StreamHandler/FileHandler` → вывод в консоль/файл.  
Не записывай в логи пароли, токены и личные данные без необходимости.
