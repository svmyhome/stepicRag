from llama_cpp import Llama

# Загрузка базовой модели + LoRA-адаптера
llm = Llama(
    model_path="../Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
    lora_path="../lora_adapter.gguf",
    n_ctx=512,
    n_threads=4,
    n_gpu_layers=0,
    verbose=False
)

# Промпт для генерации
prompt = "<s>[INST] Создай документацию для эндпоинта: получение данных о созданных задачах пользователя. Метод GET, путь /api/v1/get-user-tasks, возвращает JSON с задачами пользователя. [/INST]"

# Генерация текста
output = llm(
    prompt,
    max_tokens=256,
    temperature=0.1,
    echo=False
)

# Вывод результата
print("Ответ модели:")
print(output["choices"][0]["text"].strip())