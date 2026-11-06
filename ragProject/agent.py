import logging
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START
from typing import Annotated, TypedDict, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage

from ragProject.settings import settings
from ragProject.tools import search_docs, create_task, add_comment


# Настройка логгера
logger = logging.getLogger("agent")


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    task_id: str | None


tools = [search_docs, create_task, add_comment]
tool_node = ToolNode(tools)


# === Узел агента ===
def call_model(state: State):
    system_msg = SystemMessage(
        content=(
            "Ты — агент компании TSI. Ты можешь выполнять два типа задач:\n"
            "1. Отвечать на вопросы по внутренней документации — используй инструмент search_docs.\n"
            "2. Управлять задачами — используй create_task или add_comment, если пользователь просит создать задачу, тикет или добавить комментарий.\n"
            "\n"
            "Правила:\n"
            "- НИКОГДА не выдумывай информацию. "
            "- После search_docs прочитай результат инструмента и ответь на исходный вопрос пользователя по найденным фрагментам. "
            "Если фрагмент содержит ответ, начни с 'Информация по этому запросу в документации найдена.' и изложи ответ. "
            "Посторонние фрагменты игнорируй; если ответ уже найден, не вызывай поиск повторно.\n"
            "- Если вопрос о документации, но контекст не найден — скажи: 'Информация по этому запросу в документации не найдена.'\n"
            "- Если запрос — создать задачу или добавить комментарий — вызывай соответствующий инструмент.\n"
            "- НЕ используй search_docs для запросов вроде 'создай', 'добавь', 'зарегистрируй'."
        )
    )
    messages = [system_msg] + state["messages"]

    if state["messages"]:
        last_query = state["messages"][-1].content
        logger.info("Получен запрос", extra={"query": last_query})

    llm = ChatOllama(model=settings.ollama_model, temperature=0)
    response = llm.bind_tools(tools).invoke(messages)

    logger.info("LLM вернула ответ", extra={"has_tool_calls": bool(getattr(response, "tool_calls", []))})
    return {"messages": [response]}


# === Обновление состояния ===
def update_state(state: State):
    # Обновляем ТОЛЬКО task_id, если была создана задача
    task_id = state["task_id"]
    for msg in reversed(state["messages"]):
        if hasattr(msg, "name") and msg.name == "create_task":
            task_id = msg.content
            break
    return {"task_id": task_id}


def route_after_agent(state: State) -> Literal["tools", "__end__"]:
    """Решает: вызывать инструмент или завершить?"""
    last_msg = state["messages"][-1]
    if getattr(last_msg, "tool_calls", None):
        return "tools"
    return "__end__"


def route_after_update(state: State) -> Literal["agent", "__end__"]:
    # НЕ завершаем после search_docs — даём LLM сгенерировать ответ
    return "agent"


# Сборка графа
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_node("update", update_state)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", route_after_agent)
workflow.add_edge("tools", "update")
workflow.add_conditional_edges("update", route_after_update)

app = workflow.compile()
