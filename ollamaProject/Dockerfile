FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y build-essential cmake && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
# Установка llama-cpp-python с AVX2-оптимизацией
RUN CMAKE_ARGS="-DLLAMA_AVX2=on" pip3 install -r requirements.txt --no-cache-dir

# Копирование модели и кода
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]