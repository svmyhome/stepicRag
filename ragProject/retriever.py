from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.document_loaders import TextLoader

from ragProject.settings import settings


_retriever = None


def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    docs_dir = Path(settings.docs_dir)
    documents = []

    # Явно загружаем каждый .md файл через TextLoader
    for md_file in docs_dir.glob("*.md"):
        loader = TextLoader(str(md_file), encoding="utf-8")
        documents.extend(loader.load())

    if not documents:
        raise FileNotFoundError(f"Не найдено .md файлов в {docs_dir}")

    splitter = MarkdownTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model=settings.ollama_embedding_model)
    )
    _retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return _retriever
