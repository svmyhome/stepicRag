import psutil
from contextvars import ContextVar
from prometheus_client import Counter, Gauge, Histogram

# Метрики Prometheus
LLM_RAM_USAGE = Gauge("llm_ram_usage_bytes", "RAM, выделенная под модель")
BUCKETS = (0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 20, 30, 60, 120, 300, float("inf"))
REQUEST_KIND = ContextVar("request_kind", default="user")
LLM_INFERENCE_LATENCY = Histogram("llm_inference_latency_seconds", "Время с ожиданием очереди", ["kind"], buckets=BUCKETS)
QUEUE_TIME = Histogram("llm_queue_wait_seconds", "Ожидание очереди", ["kind"], buckets=BUCKETS)
EXECUTION_TIME = Histogram("llm_execution_seconds", "Время выполнения модели", ["kind"], buckets=BUCKETS)
QUEUED = Gauge("llm_queued_requests", "Запросы в очереди", ["kind"])
ACTIVE = Gauge("llm_active_requests", "Выполняющиеся запросы", ["kind"])
ERRORS = Counter("llm_inference_errors", "Ошибки модели", ["kind"])
TOKENS = Counter("llm_tokens", "Обработанные токены", ["kind", "direction"])
HEALTH = Gauge("llm_healthcheck_success", "Результат последней проверки модели")
HEALTH_CHECKS = Counter("llm_healthcheck", "Результаты проверок модели", ["result"])
RECOVERY = Counter("llm_recovery", "Результаты восстановления модели", ["result"])
PROCESS_RSS = Gauge("llm_process_rss_bytes", "RSS процесса")
PROCESS_CPU = Gauge("llm_process_cpu_seconds_total", "Процессорное время процесса")


class ResourceMonitor:
    def __init__(self):
        self.process = psutil.Process()
        PROCESS_RSS.set_function(lambda: self.process.memory_info().rss)
        PROCESS_CPU.set_function(lambda: sum(self.process.cpu_times()[:2]))
        self.initial_ram = self._get_ram()
        LLM_RAM_USAGE.set(0)

    def _get_ram(self) -> int:
        return self.process.memory_info().rss

    def update_ram_metric(self):
        current_ram = self._get_ram()
        model_ram = max(0, current_ram - self.initial_ram)
        LLM_RAM_USAGE.set(model_ram)
