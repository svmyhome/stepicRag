import os
from ollama import chat


def list_markdown_files(directory: str) -> list[str]:
    """Возвращает список .md файлов в директории."""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith(".md")]


def agent_query(question: str) -> str:
    # LLM получает список файлов и выбирает подходящий ===
    directory = "./docs"
    files = list_markdown_files(directory)

    if not files:
        return "Нет .md файлов в директории docs/"

    # Формируем промпт
    prompt = f"""
    Вопрос: {question}
    Доступные файлы: {files}

    Выбери ОДИН файл, который, скорее всего, описывает тему из вопроса.
    Никаких пояснений, только имя файла.
    """
    try:
        response = chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        filename = response.message.content.strip().strip('"').strip("'")

        # Проверяем, что файл действительно существует
        if filename in files:
            return filename
        else:
            return "Не удалось найти подходящий файл."

    except Exception as e:
        return f"Ошибка: {e}"


print(agent_query("Какой файл описывает RAG?"))  # rag.md