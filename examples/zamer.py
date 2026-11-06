import os
import time
import psutil
from llama_cpp import Llama


def measure_model(model_path: str, prompt: str, n_gen: int = 128):
    current_process = psutil.Process(os.getpid())

    # RAM до загрузки
    ram_before = current_process.memory_info().rss / (1024 ** 3)  # ГБ

    start_load = time.time()
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=4,
        verbose=False
    )
    load_time = time.time() - start_load
    ram_after = current_process.memory_info().rss / (1024 ** 3)

    start_gen = time.time()
    output = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=n_gen,
        temperature=0.2
    )
    gen_time = time.time() - start_gen
    text_out = output["choices"][0]["message"]["content"]

    return {
        "ram_usage_gb": round(ram_after - ram_before, 2),
        "load_time_s": round(load_time, 2),
        "latency_s": round(gen_time, 2),
        "tokens_per_sec": round(n_gen / gen_time, 1),
        "text_out": text_out
    }


prompt = (
    "Объясни, что такое RAG (Retrieval-Augmented Generation) в контексте LLM. "
    "Ответь кратко на русском, 2–3 предложения."
)

models = [
    ("Mistral-7B", "../Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"),
    ("Phi-3-mini", "../Phi-3-mini-4k-instruct-q4.gguf")
]

for label, path in models:
    m = measure_model(path, prompt)
    print(label, m)
    print("--- ответ модели ---")
    print(m["text_out"][:500])
    print()