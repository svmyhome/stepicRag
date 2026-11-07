import asyncio
import structlog
from llama_cpp import Llama
from functools import partial
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body
from concurrent.futures import ThreadPoolExecutor

logger = structlog.get_logger()

# Глобальная переменная для модели (singleton)
llm = None
executor = ThreadPoolExecutor(max_workers=1)  # один поток для inference


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте и очистка при завершении."""
    global llm
    # --- Старт приложения ---
    llm = Llama(
        model_path="./mistral-7b-instruct-v0.3-q4_k_m.gguf",
        n_ctx=2048,
        n_threads=4,
        verbose=False
    )
    logger.info("llm_loaded", model="mistral-7b", n_threads=4)

    yield

    # --- Завершение приложения ---
    global executor
    if llm is not None:
        del llm
    executor.shutdown(wait=True)
    logger.info("llm_unloaded")



app = FastAPI(lifespan=lifespan)


async def generate_text(prompt: str, max_tokens: int = 128) -> str:
    """
    Неблокирующий вызов модели через ThreadPoolExecutor.
    Inference происходит в отдельном потоке, чтобы не блокировать event loop.
    """
    loop = asyncio.get_running_loop()
    func = partial(llm, prompt, max_tokens=max_tokens, echo=False)
    result = await loop.run_in_executor(executor, func)
    return result["choices"][0]["text"]


@app.post("/generate")
async def generate(prompt: str = Body(..., embed=True)):
    try:
        answer = await asyncio.wait_for(generate_text(prompt), timeout=30.0)
        logger.info("inference_success", prompt_length=len(prompt))
        return {"answer": answer}

    except asyncio.TimeoutError:
        logger.warning("inference_timeout")
        raise HTTPException(status_code=504, detail="Model timeout")

    except Exception as e:
        logger.error("inference_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Inference error")