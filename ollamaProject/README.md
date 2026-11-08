# Дообучение модели для документации API

Датасет `api_docs_dataset.jsonl` содержит примеры с полями `instruction` и `output`. Для дообучения подготовьте такие пары для нужных эндпоинтов, разделите данные на обучающую и проверочную выборки и обучите LoRA-адаптер для Mistral-7B-Instruct-v0.3 в инструменте, поддерживающем PEFT/LoRA (например, Unsloth). Сохраните адаптер и токенизатор. Обучающего скрипта в этом каталоге нет; само объединение ниже не выполняет обучение.

В `lora_model.zip` уже сохранён адаптер в формате PEFT: его конфигурация указывает базовую модель `unsloth/mistral-7b-instruct-v0.3`. Для другого адаптера используйте ту же базовую модель и ревизию, с которыми он обучался.

## Подготовка GGUF и объединение

Команды ниже выполняются из корня репозитория. Понадобятся базовая модель `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf` и адаптер `lora_adapter.gguf`. Если есть только PEFT-адаптер из архива, распакуйте его и преобразуйте в GGUF с помощью `convert_lora_to_gguf.py` из [llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/convert_lora_to_gguf.py); для конвертации нужны зависимости этого проекта и, при необходимости, файлы исходной базовой модели.

В Ollama 0.40.15 строка `ADAPTER` вызывает `LoRA adapters are no longer supported`. Поэтому объедините адаптер с моделью до импорта. Утилита `llama-export-lora` может отсутствовать в пакете Homebrew; её можно собрать из исходников:

```bash
brew install cmake
git clone https://github.com/ggml-org/llama.cpp.git /tmp/llama-cpp
cmake -S /tmp/llama-cpp -B /tmp/llama-cpp/build
cmake --build /tmp/llama-cpp/build --target llama-export-lora -j 4
```

Если каталог `/tmp/llama-cpp` уже существует, используйте его вместо повторного клонирования. Выполните объединение:

```bash
/tmp/llama-cpp/build/bin/llama-export-lora \
  -m ./Mistral-7B-Instruct-v0.3-Q4_K_M.gguf \
  --lora ./lora_adapter.gguf \
  -o ./mistral-merged.gguf
```

Успешное выполнение заканчивается сообщением `done, output file is ./mistral-merged.gguf`. Объединение с уже квантованной моделью может снизить качество; для лучшего качества используйте базовую модель в F16 и при необходимости квантовайте результат отдельно.

## Импорт в Ollama

В корневом `Modelfile` укажите объединённый файл без директивы `ADAPTER`:

```dockerfile
FROM ./mistral-merged.gguf
```

```bash
ollama create my-api-docs -f Modelfile
ollama run my-api-docs
```

Проверьте ответы на примерах, которые не использовались при обучении. Если появляется `no space left on device`, освободите место: Ollama копирует модель в своё хранилище. Проверьте свободное место и размер файла:

```bash
df -h ~
ls -lh ./mistral-merged.gguf
ollama list
```

Ненужную модель Ollama можно удалить командой `ollama rm ИМЯ_МОДЕЛИ`. Сохраните исходную модель и адаптер, если потребуется повторное объединение.
