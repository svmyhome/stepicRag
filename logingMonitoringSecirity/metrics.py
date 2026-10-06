import time
import logging
from functools import wraps
from collections import defaultdict

from ollama import chat

# ponytail: метрики живут в памяти одного процесса; для сервиса использовать Prometheus.
_stats = defaultdict(int)      # количество событий
_totals = defaultdict(float)   # суммарные значения (например, общее время)
_errors = defaultdict(int)     # ошибки отдельно для каждой функции
logger = logging.getLogger("agent.metrics")

def observe(key: str, value: float):
    """Фиксирует одно измерение: например, latency = 1.2 сек."""
    _stats[key] += 1
    _totals[key] += value

def get_metrics() -> dict[str, dict[str, int | float]]:
    """Возвращает показатели отдельно для каждой измеряемой функции."""
    return {
        name: {
            "requests_total": count,
            "latency_avg_sec": _totals[name] / count,
            "errors_total": _errors.get(name, 0),
        }
        for name, count in _stats.items()
        if count
    }


def monitor(func):
    """Считает завершённые вызовы, включая ошибки, и измеряет их время."""
    @wraps(func)  # сохраняет имя, аннотации и описание для @tool
    def wrapper(*args, **kwargs):
        name = func.__name__
        logger.info("Начало вызова %s", name)
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        except Exception:
            _errors[name] += 1
            logger.exception("Ошибка в %s", name)  # сообщение и traceback
            raise
        finally:
            duration = time.perf_counter() - start
            observe(name, duration)
            logger.info("Вызов %s завершён за %.3f с", name, duration)
    return wrapper
@monitor
def call_llm(prompt: str) -> str:
    return chat(model="mistral", messages=[{"role": "user", "content": prompt}])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    call_llm('Ты чатбот')
    print(get_metrics())
