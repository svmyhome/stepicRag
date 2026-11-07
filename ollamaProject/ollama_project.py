import httpx
import structlog
from fastapi import FastAPI, HTTPException, Body
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

app = FastAPI()
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_API_URL = OLLAMA_BASE_URL + "/api/generate"


@retry(
    stop=stop_after_attempt(3),           # максимум 3 попытки
    wait=wait_exponential(multiplier=1, min=1, max=5)  # экспоненциальная задержка: 1с → 2с → 4с
)
async def call_ollama(model: str, prompt: str) -> dict:
    # httpx — асинхронный HTTP-клиент для Python
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,          # отключаем потоковую генерацию
                "options": {"temperature": 0.1}  # фиксируем параметры для стабильности
            }
        )
        response.raise_for_status()       # вызывает исключение при HTTP-ошибках
        return response.json()


@app.post("/generate")
async def generate(prompt: str = Body(..., embed=True)):
    model = "mistral"
    try:
        try:
            result = await call_ollama(model, prompt)
        except:
            model = "phi3"
            result = await call_ollama(model, prompt)  # резервная модель

        # Логируем только метаданные
        logger.info(
            "ollama_request_success",
            model=model,
            prompt_length=len(prompt),
            eval_duration_ms=result.get("eval_duration", 0) // 1_000_000  # время генерации в мс
        )
        return {"answer": result["response"]}

    except Exception as e:
        logger.error("ollama_request_failed", error=str(e), model=model)
        raise HTTPException(status_code=502, detail="LLM service unavailable")


@app.get("/health")
async def health():
    """
    Healthcheck — эндпоинт для проверки работоспособности сервиса.
    Используется оркестраторами (например, Kubernetes) для перезапуска
    недоступных компонентов.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Проверяем, отвечает ли Ollama на базовый запрос
            await client.get(OLLAMA_BASE_URL)
        return {"status": "healthy"}
    except Exception as e:
        logger.error("healthcheck_failed", error=str(e))
        return {"status": "unhealthy"}