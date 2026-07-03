from datetime import date
from typing import Optional

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.mixins import IdPkMixin


class Employee(IdPkMixin, Base):
    __tablename__ = "employees"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)

    phone: Mapped[Optional[str]] = mapped_column(
        String(15), unique=True, index=True, nullable=True
    )
    photo_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
