# UV: базовые команды

## Установка и обновление UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # установить uv (macOS/Linux)
uv self update                                  # обновить uv
uv --version                                    # проверить установку
```

## Создание и инициализация проекта

```bash
uv init my-project              # создать новый проект
cd my-project
uv init                         # инициализировать текущую пустую папку
uv python install 3.14          # установить нужную версию Python
uv venv --python 3.14           # создать виртуальное окружение .venv
```

В этом проекте требуется Python 3.14 или новее (`pyproject.toml`).

## Зависимости

```bash
uv add requests                 # добавить зависимость в проект
uv add --dev pytest             # добавить зависимость только для разработки
uv remove requests              # удалить зависимость
uv sync                         # установить зависимости из uv.lock в .venv
uv lock --upgrade               # обновить версии всех зависимостей в lock-файле
uv lock --upgrade-package requests # обновить только одну зависимость
```

После изменения `pyproject.toml` обычно достаточно выполнить `uv sync`.

## Запуск и инструменты

```bash
uv run python main.py           # запустить скрипт в окружении проекта
uv run pytest                   # запустить тесты
uv run ruff check .             # запустить установленный в проекте линтер
uv tool run ruff check .        # разово запустить инструмент без добавления в проект
```

`uv run` сам синхронизирует окружение при необходимости; активировать `.venv` вручную не нужно.

## Полезное

```bash
uv python list                  # показать доступные версии Python
uv tree                         # показать дерево зависимостей
uv export --format requirements-txt -o requirements.txt  # экспортировать зависимости
```
