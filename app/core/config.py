from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appointment_db"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/appointment_db"
    
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    return Settings()
