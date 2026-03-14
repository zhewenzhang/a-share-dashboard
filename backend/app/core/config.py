from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    tushare_token: str = ""
    database_url: str = "sqlite:///./data/ashare.db"
    backend_url: str = "http://localhost:8000"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
