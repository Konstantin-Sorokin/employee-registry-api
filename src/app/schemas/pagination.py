from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    """Универсальная схема ответа с пагинацией."""

    items: list[T] = Field(..., description="Список объектов")
    total: int = Field(..., ge=0, description="Общее количество записей")
    page: int = Field(..., ge=1, description="Текущая страница")
    limit: int = Field(..., ge=1, description="Записей на странице")
    pages: int = Field(..., ge=0, description="Всего страниц")
