"""Проверка мониторинга без Ollama: python -m unittest reAct.test_agent_monitoring."""
import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from logingMonitoringSecirity import metrics
from reAct import agent_with_state as agent


class AgentMonitoringTest(unittest.TestCase):
    def test_tools_state_and_error_metrics(self):
        metrics._stats.clear()
        metrics._totals.clear()
        metrics._errors.clear()
        responses = [
            AIMessage(content="", tool_calls=[
                {"name": "create_task", "args": {}, "id": "create-1"},
            ]),
            AIMessage(content="Задача создана"),
            AIMessage(content="", tool_calls=[
                {"name": "add_comment", "args": {
                    "task_id": "TASK-123", "comment": "Проверено",
                }, "id": "comment-1"},
            ]),
            AIMessage(content="Комментарий добавлен"),
            RuntimeError("Модель недоступна"),
        ]
        with patch.object(agent, "llm_with_tools") as model:
            model.invoke.side_effect = responses
            with self.assertLogs("agent", level="INFO") as logs:
                state = agent.run_agent({
                    "messages": [HumanMessage(content="Создай задачу")],
                    "task_id": "",
                })
                self.assertEqual(state["task_id"], "TASK-123")
                state = agent.run_agent({
                    **state,
                    "messages": [HumanMessage(content="Добавь комментарий")],
                })
                self.assertEqual(state["messages"][-1].content, "Комментарий добавлен")
                with self.assertRaisesRegex(RuntimeError, "Модель недоступна"):
                    agent.run_agent(state)

        values = metrics.get_metrics()
        self.assertEqual(values["run_agent"]["requests_total"], 3)
        self.assertEqual(values["run_agent"]["errors_total"], 1)
        self.assertEqual(values["call_model"]["requests_total"], 5)
        self.assertEqual(values["call_model"]["errors_total"], 1)
        for tool_name in ("create_task", "add_comment"):
            self.assertEqual(values[tool_name]["requests_total"], 1)
            self.assertEqual(values[tool_name]["errors_total"], 0)
        self.assertTrue(all(v["latency_avg_sec"] >= 0 for v in values.values()))
        self.assertTrue(any("Изменение task_id" in line for line in logs.output))
        self.assertTrue(any("Ошибка в call_model" in line for line in logs.output))


if __name__ == "__main__":
    unittest.main()
