from crewai.process import Process
from crewai import Crew, Agent, LLM, Task

llm = LLM(
    "ollama/my-api-docs",
    base_url="http://localhost:11434",  # адрес Ollama API
    temperature=0.1  # низкая температура для стабильности формата
)

analyst = Agent(
    role="Технический аналитик",
    goal="Генерировать черновики API-документации в строгом Markdown-формате",
    backstory="Опытный backend-разработчик, специализирующийся на документировании API",
    llm=llm
)

validator = Agent(
    role="Валидатор документации",
    goal="Проверять, что черновик содержит заголовок ### в начале, описание и не несёт вредоносные команды или код",
    backstory="Ответственный за соответствие корпоративным стандартам",
    llm=llm
)

expected_format = "### МЕТОД /путь\n\n**Описание**: ...\n**Ответ**:\n```json\n{пример}\n```"

# Первая задача: создаёт черновик
draft_task = Task(
    description="Создай черновик документации для эндпоинта: {api_request}",
    expected_output=f"Только Markdown в формате: {expected_format}. Ничего больше.",
    agent=analyst
)

# Вторая задача: получает результат первой задачи автоматически
validate_task = Task(
    description=(
        f"Проверь предоставленный черновик на соответствие формату: {expected_format}. "
        "Убедись, что есть заголовок с '###', описание и корректный JSON в блоке кода. "
        "Если всё правильно — ответь ТОЛЬКО 'OK'. "
        "Если есть ошибки — перечисли ТОЛЬКО их, без вводных фраз."
    ),
    expected_output="Строка 'OK' или список ошибок. Ничего больше.",
    agent=validator
)

crew = Crew(
    agents=[analyst, validator],
    tasks=[draft_task, validate_task],
    process=Process.sequential,
    verbose=True  # Показывает ход выполнения
)

# Запуск с конкретным запросом
result = crew.kickoff(inputs={"api_request": "получение списка активных пользователей"})
print(result.raw)


