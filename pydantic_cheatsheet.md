# Pydantic v2: выжимка

Pydantic берёт внешние данные (`dict`, JSON, переменные окружения), проверяет их и создаёт объект с гарантированными типами.

## 1. Модель

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int              # обязательно
    name: str = "Guest"  # необязательно: есть значение по умолчанию

user = User(id="42")
assert user.id == 42     # строка преобразована в int
```

Аннотация типа — правило проверки. Значение по умолчанию делает поле необязательным.

## 2. Ограничения поля

```python
from pydantic import Field

class Product(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    discount: int | None = Field(default=None, ge=0, le=100)
```

Главные ограничения: `gt/ge/lt/le`, `min_length/max_length`, `pattern`. `description` попадёт в OpenAPI/JSON Schema.

## 3. Вложенные модели и списки

```python
class Address(BaseModel):
    city: str

class User(BaseModel):
    name: str
    address: Address
    tags: list[str] = Field(default_factory=list)

user = User(name="Анна", address={"city": "Москва"})
user = User.model_validate_json('{"name": "Анна", "address": {"city": "Москва"}}')
```

Pydantic сам превратит словарь в `Address`. Для изменяемых значений по умолчанию используй `default_factory`.

## 4. Проверка данных

```python
user = User.model_validate({"name": "Анна", "address": {"city": "Москва"}})
user = User.model_validate_json('{"name": "Анна", "address": {"city": "Москва"}}')
```

`User(...)` и `model_validate(...)` проверяют Python-данные. Для JSON используй `model_validate_json()`.

## 5. Результат и ошибки

```python
from pydantic import ValidationError

try:
    User.model_validate({"name": 123})
except ValidationError as error:
    print(error.errors())  # список ошибок: поле, причина, входное значение

data = user.model_dump()          # dict
json_text = user.model_dump_json() # JSON-строка
schema = User.model_json_schema() # схема для OpenAPI
```

## 6. Валидатор: правило, которого нет в типах

```python
from pydantic import field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Имя не должно быть пустым")
        return value.strip().title()
```

`field_validator` — для одного поля. Если правило сравнивает несколько полей, используй `@model_validator(mode="after")`.

## 7. Запрет лишних полей

```python
from pydantic import ConfigDict

class User(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
```

`extra="forbid"` полезен для API и конфигурации: опечатка во входных данных станет ошибкой. По умолчанию лишние поля игнорируются.

## 8. Строгий режим

```python
class StrictUser(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int

StrictUser(id="42")  # ошибка: строка не станет int
```

Обычно преобразование типов удобно. `strict=True` включай на границе, где важен именно исходный тип.

## 9. Настройки приложения

Для `.env` применяется `BaseSettings` из `pydantic-settings` — это уже используется в [`settings.py`](settings.py):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    qdrant_port: int
    model_config = SettingsConfigDict(env_file=".env")
```

`QDRANT_PORT=6333` будет прочитан из окружения и превращён в `int`.

## Запомнить

`BaseModel` + аннотации → структура и типы.  
`Field` → ограничения.  
`model_validate*` → входные данные.  
`model_dump*` → выходные данные.  
`ValidationError` → показать пользователю/клиенту, что именно неверно.  
`BaseSettings` → те же правила для окружения и `.env`.
