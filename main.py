from ollama import AsyncClient
from fastapi import FastAPI, Body
from contextlib import asynccontextmanager
from qdrant_client import AsyncQdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance, PointStruct

from settings import settings

# Инициализация моделей и клиентов (один раз при старте)
embedding_model = SentenceTransformer(settings.embedding_model)
qdrant = AsyncQdrantClient(settings.qdrant_host, port=settings.qdrant_port)
ollama = AsyncClient(host=settings.ollama_host)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при запуске и очистка при завершении"""
    global embedding_model, qdrant

    # --- Startup ---
    if await qdrant.collection_exists(settings.collection_name):
        await qdrant.delete_collection(settings.collection_name)

    await qdrant.create_collection(
        collection_name=settings.collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    docs = [
        "FastAPI — это современный Python-фреймворк для создания API.",
        "Liquibase используется для управления миграциями базы данных.",
        "Docker упрощает развёртывание приложений через контейнеризацию."
    ]
    embeddings = embedding_model.encode(docs)
    points = [
        PointStruct(id=i, vector=emb.tolist(), payload={"text": doc})
        for i, (doc, emb) in enumerate(zip(docs, embeddings))
    ]

    await qdrant.upsert(settings.collection_name, points)
    print(f"✅ Коллекция '{settings.collection_name}' создана и заполнена.")

    yield  # <-- запуск приложения

    # --- Shutdown (опционально) ---
    # Например, закрытие соединений
    await qdrant.delete_collection(settings.collection_name)
    await qdrant.close()


# Старт сервиса
app = FastAPI(title="RAG Service", lifespan=lifespan)


@app.post("/ask")
async def ask(question: str = Body(..., embed=True)):
    """
    RAG-эндпоинт: получает вопрос → возвращает ответ от LLM с контекстом.
    """
    # 1. Эмбеддинг запроса
    query_vector = embedding_model.encode(question).tolist()

    # 2. Поиск в Qdrant (асинхронно)
    search_result = await qdrant.query_points(
        collection_name=settings.collection_name,
        query=query_vector,
        limit=1
    )
    context = search_result.points[0].payload["text"]
    # 3. Генерация ответа через Ollama (асинхронно)
    prompt = f"""
    Отвечай только на основе контекста. Если не знаешь — скажи "Не знаю".
    Контекст: {context}
    Вопрос: {question}
    """
    response = await ollama.chat(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1}
    )
    return {"answer": response.message.content}