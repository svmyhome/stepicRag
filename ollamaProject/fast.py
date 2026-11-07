from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from engine import LocalLlmEngine
from health import deep_healthcheck
from recovery import SelfHealingEngine
from prometheus_client import make_asgi_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with LocalLlmEngine("./Mistral-7B-Instruct-v0.3-Q4_K_M.gguf") as engine:
        app.state.llm = SelfHealingEngine(engine)
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health_check(request: Request):
    healthy = await deep_healthcheck(request.app.state.llm)
    return {"status": "healthy" if healthy else "unhealthy"}

@app.post("/generate")
async def generate(prompt: str, request: Request):
    answer = await request.app.state.llm.generate(prompt)
    return {"answer": answer}