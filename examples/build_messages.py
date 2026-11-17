def build_messages(system_prompt: str, history: list[dict], user_text: str, max_history: int) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt}]

    if max_history > 0:
        # Берем последние max_history сообщений (срез не меняет исходный список)
        recent_history = history[-max_history:]

        # Находим индекс первого сообщения "user" (пропускаем "assistant" в начале)
        start_idx = 0
        while start_idx < len(recent_history) and recent_history[start_idx]["role"] == "assistant":
            start_idx += 1

        # Добавляем оставшуюся часть истории (если что-то осталось)
        messages.extend(recent_history[start_idx:])

    # Добавляем новое сообщение клиента
    messages.append({"role": "user", "content": user_text})

    return messages


print(build_messages(
    "Отвечай кратко.",
    [
        {"role": "user", "content": "Где заказ 5512?"},
        {"role": "assistant", "content": "Передан в доставку."},
        {"role": "user", "content": "А когда привезут?"},
        {"role": "assistant", "content": "Завтра до 18:00."}
    ],
    "Можно перенести на субботу?",
    2
))

# → [
#     {"role": "system", "content": "Отвечай кратко."},
#     {"role": "user", "content": "А когда привезут?"},
#     {"role": "assistant", "content": "Завтра до 18:00."},
#     {"role": "user", "content": "Можно перенести на субботу?"}
# ]
