import json
from collections.abc import Callable
from typing import Any

import ollama


class ReActAgent:
    def __init__(self, llm: Callable[[str], str], tools: dict[str, Callable[..., Any]]):
        self.llm = llm
        self.tools = tools
        self.state: dict[str, Any] = {"history": [], "done": False, "error_count": 0}

    def reason(self) -> dict[str, Any]:
        prompt = f"""
        Состояние: {json.dumps(self.state, ensure_ascii=False)[:1000]}
        Инструменты: {list(self.tools.keys())}

        Что сделать следующим шагом? Верни строго валидный JSON:
        {{"action": "tool_name", "params": {{...}}, "thought": "почему"}}
        Или {{"action": "finish", "result": "итоговый ответ"}}
        Если в history уже есть успешный result, используй его и заверши задачу через finish.
        Не вызывай повторно инструмент, результат которого уже есть в history.
        """
        response = self.llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"action": "finish", "result": f"Ошибка парсинга ответа LLM: {response}"}

    def act(self, decision: dict[str, Any]) -> dict[str, Any] | None:
        if decision.get("action") == "finish":
            self.state["done"] = True
            self.state["result"] = decision.get("result")
            return None

        tool_name = decision.get("action")
        params = decision.get("params", {})

        if not isinstance(tool_name, str) or tool_name not in self.tools:
            return {"action": tool_name, "error": f"Инструмент '{tool_name}' не найден"}

        try:
            result = self.tools[tool_name](**params)
            return {"action": tool_name, "result": result, "error": None}
        except Exception as e:
            return {"action": tool_name, "error": f"Ошибка выполнения: {e}"}

    def observe(self, action_result: dict[str, Any] | None) -> None:
        if action_result is None:
            return

        self.state["history"].append(action_result)

        if action_result.get("error"):
            self.state["error_count"] = self.state.get("error_count", 0) + 1
            if self.state["error_count"] >= 3:
                self.state["done"] = True
                self.state["result"] = "Превышен лимит ошибок"
        else:
            self.state["error_count"] = 0

    def run(self, task: str, max_steps: int = 5) -> str:
        self.state["task"] = task
        self.state["done"] = False
        self.state["error_count"] = 0

        for step in range(max_steps):
            if self.state["done"]:
                break

            decision = self.reason()
            action_result = self.act(decision)
            self.observe(action_result)

        return self.state.get("result", "Лимит шагов исчерпан без результата")


def check_database_metrics(service: str) -> dict[str, Any]:
    """
    Получает метрики базы данных для указанного сервиса.
    Идемпотентен: одинаковые параметры дают одинаковый результат.
    """
    # В реальности здесь будет запрос к БД или мониторингу
    mock_data = {
        "payment": {"latency_ms": 450, "connections": 95, "errors": 12},
        "auth": {"latency_ms": 120, "connections": 40, "errors": 1},
    }
    return mock_data.get(service, {"error": f"Сервис '{service}' не найден"})


def ask_mistral(prompt: str) -> str:
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        format="json",
    )
    return response.message.content or ""


if __name__ == "__main__":
    agent = ReActAgent(ask_mistral, {"check_database_metrics": check_database_metrics})
    print(agent.run("Проверь метрики базы данных сервиса payment и объясни проблему"))
