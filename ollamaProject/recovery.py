from engine import LocalLlmEngine
from metrics import RECOVERY


class SelfHealingEngine:
    def __init__(self, engine: LocalLlmEngine, max_failures: int = 3):
        self._engine = engine
        self._failures = 0
        self._max_failures = max_failures

    async def generate(self, prompt: str, max_tokens: int = 128) -> str:
        if self._failures >= self._max_failures:
            await self._recover()

        try:
            return await self._engine.generate(prompt, max_tokens)
        except Exception:
            self._failures += 1
            raise

    async def _recover(self):
        """Перезагружает модель в новом контексте."""
        # Выгружаем старую
        try:
            await self._engine.__aexit__(None, None, None)
            await self._engine.__aenter__()
        except Exception:
            RECOVERY.labels("error").inc()
            raise
        RECOVERY.labels("success").inc()
        self._failures = 0
