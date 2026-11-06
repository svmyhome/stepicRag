import chromadb
from chromadb.utils import embedding_functions


documents = [
    "FastAPI — это современный Python-фреймворк для создания API.",
    "Alembic — это инструмент для управления миграциями базы данных в SQLAlchemy.",
    "Общий ответ."
]

metadatas = [
    {"team": "docs"},
    {"team": "backend"},
    {"team": "all"}
]

query, user_team = (part.strip() for part in input().rsplit(",", 1))

client = chromadb.Client()
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.create_collection(
    name="team_documents",
    embedding_function=embedding_function,
)
collection.add(
    ids=["1", "2", "3"],
    documents=documents,
    metadatas=metadatas,
)

results = collection.query(
    query_texts=[query],
    n_results=1,
    where={"team": {"$in": [user_team, "all"]}},
)
print(results["documents"][0][0])
