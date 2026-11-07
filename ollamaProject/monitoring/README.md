# Мониторинг локальной модели

На macOS с Docker Desktop сначала запустите приложение из корня проекта:

```bash
PYTHONPATH=ollamaProject uv run uvicorn fast:app --host 0.0.0.0 --port 8000
```

Адрес `0.0.0.0` позволяет контейнеру обратиться к приложению через `host.docker.internal`; приложение также будет доступно другим устройствам в сети, если это разрешает брандмауэр. Сервер не настроен на аутентификацию.

В другом терминале запустите мониторинг:

```bash
docker compose -f ollamaProject/monitoring/compose.yaml up -d
```

Откройте Grafana: http://localhost:3000 (первый вход: `admin` / `admin`, затем смените пароль). Дашборд **Local LLM** и источник Prometheus загружаются автоматически. Prometheus доступен на http://localhost:9090/targets — у `local_llm` должен быть статус UP. Метрики собираются каждые 10 секунд; графикам скорости нужны как минимум два измерения. Выполните несколько запросов через http://localhost:8000/docs.

Остановить мониторинг, сохранив историю:

```bash
docker compose -f ollamaProject/monitoring/compose.yaml down
```

RAM — разница RSS процесса после загрузки, а не точный расход модели. Успешный `/health` также считается генерацией. `up` проверяет получение метрик, а не работоспособность inference.
