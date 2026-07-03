from datetime import date
from typing import Literal, Optional

from pydantic import Field, field_validator

from app.schemas.mixins import IdMixin, NameStripMixin, OrmMixin

PHONE_PATTERN = r"^\d{11}$"


class EmployeeBase(NameStripMixin):
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    middle_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Отчество"
    )

    birth_date: date = Field(..., description="Дата рождения")
    gender: Literal["Male", "Female"] = Field(..., description="Пол")

    phone: Optional[str] = Field(None, description="Телефон")
    photo_filename: Optional[str] = Field(None, description="Фото: Имя файла")

    @field_validator("birth_date", mode="before")
    @classmethod
    def validate_birth_date(cls, v):
        if isinstance(v, date) and v > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
        return v


class EmployeeCreate(EmployeeBase):
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)


class EmployeeUpdate(EmployeeBase):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)

    birth_date: Optional[date] = None
    gender: Optional[Literal["Male", "Female"]] = Field(None)

    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)


class EmployeeResponse(OrmMixin, IdMixin, EmployeeBase):
    pass
