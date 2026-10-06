import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel
from ragas.llms import llm_factory
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextRelevance

# === Датасет ===
dataset = EvaluationDataset(samples=[
    SingleTurnSample(
        user_input="Какой инструмент используется для миграций базы данных?",
        response="Для миграций базы данных используется Alembic.",
        retrieved_contexts=["Alembic используется для управления миграциями базы данных в SQLAlchemy."]
    ),
    SingleTurnSample(
        user_input="Что такое FastAPI?",
        response="FastAPI — это современный Python-фреймворк для создания API.",
        retrieved_contexts=["FastAPI — это современный Python-фреймворк для создания API."]
    )
])

# === LLM и Embeddings ===
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
llm = llm_factory("mistral", client=client)
embeddings = HuggingFaceEmbeddings(model="all-MiniLM-L6-v2")

# === Модель результата ===
class Result(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_relevance: float

# === Оценка одной строки ===
async def evaluate_sample(sample: SingleTurnSample) -> Result:
    faith = await Faithfulness(llm=llm).ascore(
        user_input=sample.user_input,
        response=sample.response,
        retrieved_contexts=sample.retrieved_contexts
    )
    ar = await AnswerRelevancy(llm=llm, embeddings=embeddings).ascore(
        user_input=sample.user_input,
        response=sample.response
    )
    cr = await ContextRelevance(llm=llm, embeddings=embeddings).ascore(
        user_input=sample.user_input,
        retrieved_contexts=sample.retrieved_contexts
    )
    return Result(
        faithfulness=faith.value,
        answer_relevancy=ar.value,
        context_relevance=cr.value
    )

# === Запуск ===
async def main():
    for i, sample in enumerate(dataset.samples):
        res = await evaluate_sample(sample)
        print(f"Sample {i+1}: {res}")

if __name__ == "__main__":
    asyncio.run(main())