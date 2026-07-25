import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CHROMA_DB_DIR: str = "./data/chroma"
    SQLITE_DB_PATH: str = "sqlite:///./data/maha_gr.db"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    class Config:
        env_file = ".env"

settings = Settings()
