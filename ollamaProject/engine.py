import asyncio
import time
from llama_cpp import Llama
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from metrics import (ResourceMonitor, LLM_INFERENCE_LATENCY, REQUEST_KIND, QUEUE_TIME,
                     EXECUTION_TIME, QUEUED, ACTIVE, ERRORS, TOKENS)


class LocalLlmEngine:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 4):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self._llm: Llama | None = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._monitor = ResourceMonitor()

    async def __aenter__(self):
        # Временный пул ТОЛЬКО для загрузки
        with ThreadPoolExecutor(max_workers=1) as temp_executor:
            loop = asyncio.get_running_loop()
            self._llm = await loop.run_in_executor(
                temp_executor,
                partial(Llama, self.model_path, n_ctx=self.n_ctx, n_threads=self.n_threads, verbose=False)
            )
        self._monitor.update_ram_metric()

        # Теперь создаём основной пул для inference
        self._executor = ThreadPoolExecutor(max_workers=1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._llm is not None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(self._executor, self._cleanup_llm)
        if not self._executor._shutdown:
            self._executor.shutdown(wait=True)

    def _cleanup_llm(self):
        # Всё освобождение — в синхронном методе
        if self._llm is not None:
            del self._llm
            self._llm = None

    async def generate(self, prompt: str, max_tokens: int = 128) -> str:
        if self._llm is None:
            raise RuntimeError("Model not loaded")

        start = time.monotonic()
        kind = REQUEST_KIND.get()
        model = self._llm
        QUEUED.labels(kind).inc()

        def run():
            QUEUED.labels(kind).dec()
            ACTIVE.labels(kind).inc()
            started = time.monotonic()
            QUEUE_TIME.labels(kind).observe(started - start)
            try:
                result = model(prompt, max_tokens=max_tokens, echo=False)
                text = result["choices"][0]["text"]
                duration = time.monotonic() - started
                EXECUTION_TIME.labels(kind).observe(duration)
                LLM_INFERENCE_LATENCY.labels(kind).observe(time.monotonic() - start)
                usage = result.get("usage", {})
                for key, direction in (("prompt_tokens", "input"), ("completion_tokens", "output")):
                    if key in usage:
                        TOKENS.labels(kind, direction).inc(usage[key])
                return text
            except Exception:
                ERRORS.labels(kind).inc()
                raise
            finally:
                ACTIVE.labels(kind).dec()

        try:
            try:
                future = self._executor.submit(run)
            except Exception:
                QUEUED.labels(kind).dec()
                ERRORS.labels(kind).inc()
                raise
            future.add_done_callback(lambda f: QUEUED.labels(kind).dec() if f.cancelled() else None)
            return await asyncio.wrap_future(future)
        except Exception as e:
            raise RuntimeError(f"Inference failed: {e}") from e
