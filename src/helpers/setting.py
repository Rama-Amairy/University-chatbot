import os
import json
from typing import List, Optional
from pydantic_settings import BaseSettings

# Define root_dir relative to this file
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class Settings(BaseSettings):
    # ✅ Application Settings
    APP_NAME: str
    APP_VERSION: str

    LOC_DOC: str

    VECTOR_DB: str
    SQLITE_DB: str
    PORT: int

    HOST: str
    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    EMBEDDING_MODEL: str
    HUGGINGFACE_TOKIENS: str
    HUGGINGFACE_MODEL_NAME: Optional[str] = None
    
    class Config:
        env_file = os.path.join(root_dir, ".env")
        env_file_encoding = "utf-8"

# Singleton-style getter (FastAPI friendly)
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()
