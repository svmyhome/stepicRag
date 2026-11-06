import logging
import re

from langchain_core.tools import tool

from ragProject.retriever import get_retriever

logger = logging.getLogger("agent")


@tool
def search_docs(query: str) -> str:
    """
    Ищет информацию в документации по запросу.
    Возвращает ТОЛЬКО релевантные фрагменты текста.
    Если ничего не найдено — возвращает сообщение об этом.
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)

        if not docs:
            logger.debug("Поиск не вернул результатов")
            return "Информация по запросу не найдена в документации."

        # Собираем ТОЛЬКО содержимое, без метаданных
        contents = [doc.page_content.strip() for doc in docs if doc.page_content.strip()]

        if not contents:
            return "Информация по запросу не найдена в документации."

        result = "\n\n".join(contents)
        logger.debug("Найдены релевантные фрагменты", extra={"fragments": contents})
        return result

    except Exception as e:
        logger.error("Ошибка в search_docs", extra={"error": str(e)})
        return "Не удалось выполнить поиск в документации."


@tool
def create_task(description: str) -> str:
    """Создаёт задачу в трекере. Возвращает ID в формате TSI-123."""
    if not description or not description.strip():
        raise ValueError("Описание задачи не может быть пустым")
    return "TSI-777"


@tool
def add_comment(task_id: str, comment: str) -> str:
    """Добавляет комментарий к задаче."""
    if not re.match(r"^TSI-\d+$", task_id):
        raise ValueError("Неверный формат task_id")
    if not comment or not comment.strip():
        raise ValueError("Комментарий не может быть пустым")
    return f'Комментарий добавлен к задаче {task_id}'
