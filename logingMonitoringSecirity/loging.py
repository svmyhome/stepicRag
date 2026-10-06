import hashlib
import logging

# Настраиваем базовое логирование
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agent")


def log_prompt(prompt: str) -> str:
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
    logger.debug(f"Промпт (хэш: {prompt_hash}) отправлен в LLM")
    return prompt_hash


def agent_step(user_query: str, user_id: str) -> str:
    logger.info(f"Запрос от user_id={user_id}: {user_query!r}")

    # Предположим, retrieve() — это RAG-поиск
    chunks = retrieve(user_query)
    logger.debug(f"Найдено {len(chunks)} релевантных чанков")

    prompt = build_prompt(chunks, user_query)
    log_prompt(prompt)

    response = call_llm(prompt)
    logger.info(f"Ответ для user_id={user_id} сгенерирован")
    return response


def retrieve(query: str) -> str:
    return 'STR NEW'


def build_prompt(chunks: list, query: str) -> str:
    return 'BUILD prompt'
def call_llm(prompt: str) -> str:
    return 'Call LLM1'

agent_step('My custom string', '123')


