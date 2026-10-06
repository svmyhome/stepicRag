import chromadb
import ollama
from chromadb.utils import embedding_functions

# === 1. Подготовка документов (ваши приватные данные) ===
# Это может быть: README, внутренняя wiki, Jira-описания, чек-листы.
# Важно: каждый элемент — независимый семантический фрагмент (чанк).
docs = [
    "FastAPI — это современный Python-фреймворк для создания API.",
    "Liquibase используется для управления миграциями базы данных.",
    "Docker упрощает развёртывание приложений через контейнеризацию."
]

# === 2. Настройка embedding-функции (ключевой компонент RAG) ===
# Используем специализированную модель для семантического поиска.
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# === 3. Сохранение в векторную БД Chroma (индексация) ===
client = chromadb.Client()

# Создаём коллекцию — аналог таблицы в реляционной БД.
# embedding_function автоматически преобразует документы в векторы при добавлении.
collection = client.create_collection(
    name="docs",
    embedding_function=ef  # Указываем, какую модель использовать для эмбеддингов
)

# Добавляем документы. Chroma:
# - вызовет ef.encode() для каждого документа,
# - сохранит вектор + исходный текст.
collection.add(
    ids=[f"id_{i}" for i in range(len(docs))],
    documents=docs
)


# === 4. Функция RAG-ответа (выполняется при каждом запросе) ===
def ask_rag(question: str) -> str:
    """
    Полный цикл RAG:
    1. Преобразовать вопрос в embedding (автоматически через ef),
    2. Найти самый релевантный фрагмент в Chroma,
    3. Передать его в LLM как контекст,
    4. Вернуть ответ от LLM.
    """
    # Шаг 1-2: семантический поиск
    # Chroma автоматически преобразует question в embedding той же моделью (ef),
    # затем ищет ближайший вектор и возвращает исходный текст.
    results = collection.query(
        query_texts=[question],
        n_results=1
    )
    context = results["documents"][0][0]

    # Шаг 3: генерация ответа через локальную LLM
    # Используем Ollama — локальный инференс без облака.
    # Mistral здесь работает ТОЛЬКО как генератор текста.
    # Она НЕ участвует в создании эмбеддингов!
    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system",
             "content": "Отвечай только на основе следующего контекста. Если не знаешь ответа — скажи 'Не знаю'."},
            {"role": "user", "content": f"Контекст: {context}\n\nВопрос: {question}"}
        ],
        options={
            "temperature": 0.1
        }
    )
    return response.message.content


config = {'doc_embedding_model': 'all-MiniLM-L6-v2', 'query_embedding_model': 'all-MiniLM-L6-v2',
          'llm_model': 'mistral'}


def is_valid_rag_config(config: dict) -> bool:
    required_keys = {
        "doc_embedding_model",
        "query_embedding_model",
        "llm_model",
    }

    if not required_keys.issubset(config):
        return False

    return (
        config["doc_embedding_model"] == config["query_embedding_model"]
        and config["doc_embedding_model"] != config["llm_model"]
    )


# === 4. Тест: запуск и проверка ===
if __name__ == "__main__":
    # Задаём вопрос, который явно ссылается на один из документов
    question = "Какой инструмент для миграций упомянут в документации?"
    answer = ask_rag(question)
    print(f"Вопрос: {question}")
    print(f"Ответ: {answer}")

    question = "Каким иснструментом развернуть приложение по нашей документации?"
    answer = ask_rag(question)
    print(f"Вопрос: {question}")
    print(f"Ответ: {answer}")

    print(is_valid_rag_config(config))
