import asyncio
from typing import Protocol
from metrics import REQUEST_KIND, HEALTH, HEALTH_CHECKS


class LLMEngine(Protocol):
    async def generate(self, prompt: str, max_tokens: int) -> str:
        ...


async def deep_healthcheck(engine: LLMEngine, timeout: float = 5.0) -> bool:
    """
    Проверяет, может ли модель выполнить inference за заданное время.
    """
    token = REQUEST_KIND.set("health")
    try:
        await asyncio.wait_for(
            engine.generate("Ping", max_tokens=5),
            timeout=timeout
        )
        HEALTH.set(1)
        HEALTH_CHECKS.labels("success").inc()
        return True
    except asyncio.TimeoutError:
        HEALTH.set(0)
        HEALTH_CHECKS.labels("timeout").inc()
        return False
    except Exception:
        HEALTH.set(0)
        HEALTH_CHECKS.labels("error").inc()
        return False
    finally:
        REQUEST_KIND.reset(token)
