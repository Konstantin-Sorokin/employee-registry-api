from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
UPLOAD_DIR = PROJECT_ROOT / "uploads" / "photos"


class RunConfig(BaseModel):
    """
    Конфигурация для запуска сервера приложения.
    Определяет параметры хоста и порта для запуска FastAPI приложения.
    """

    host: str = "0.0.0.0"
    port: int = 8000


class ApiConfig(BaseModel):
    """Конфигурация API маршрутов."""

    prefix: str = "/api"
    employees_prefix: str = "/employees"


class DatabaseConfig(BaseModel):
    """Конфигурация подключения к базе данных."""

    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class Settings(BaseSettings):
    """
    Основные настройки приложения.

    Загружает конфигурацию из переменных окружения и файлов .env.
    Использует pydantic-settings для валидации и парсинга настроек.
    """

    model_config = SettingsConfigDict(
        env_file=(
            PROJECT_ROOT / ".env.example",
            PROJECT_ROOT / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig


settings = Settings()
