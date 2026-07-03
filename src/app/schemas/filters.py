from typing import Literal, Optional

from pydantic import BaseModel, Field


class EmployeeFilter(BaseModel):
    """Параметры для фильтрации и поиска сотрудников."""

    phone: Optional[str] = Field(None, description="Номер телефона")

    search: Optional[str] = Field(None, description="Поиск по ФИО")
    gender: Optional[Literal["Male", "Female"]] = Field(
        None, description="Пол сотрудника"
    )
    age_from: Optional[int] = Field(None, ge=0, le=150, description="Возраст от")
    age_to: Optional[int] = Field(None, ge=0, le=150, description="Возраст до")
