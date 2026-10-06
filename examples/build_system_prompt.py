def build_system_prompt(task_id: str) -> str:
    if task_id.strip():
        return f'Ты — агент управления задачами. Текущий task_id: {task_id}. Если задача не создана — сначала вызови create_task. Не выдумывай ID.'
    return 'Ты — агент управления задачами. Текущий task_id: не задан. Если задача не создана — сначала вызови create_task. Не выдумывай ID.'


def validate_agent_state(state: dict) -> bool:
    return (
            isinstance(state.get("messages"), list)
            and isinstance(state.get("task_id"), str)
    )


def update_agent_state(current_state: dict, tool_result: dict) -> dict:
    if isinstance(tool_result, dict) and isinstance(current_state, dict):
        if tool_result.get("action") == "create_task":
            current_state["task_id"] = tool_result.get("result")
        return current_state
    return {'not dict': 'not dict'}

#     Если tool_result["action"] == "create_task", обновить current_state["task_id"] значением из tool_result["result"],
# Во всех остальных случаях — оставить current_state["task_id"] без изменений.

print(update_agent_state({"task_id": '123'},{"action":"create_task", 'result': '234'}))