from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    ollama_model: str = 'llama3.1'
    ollama_embedding_model: str = 'nomic-embed-text'
    docs_dir: str = str(Path(__file__).resolve().parent / 'docs')
    log_level: str = 'INFO'

settings = Settings()
