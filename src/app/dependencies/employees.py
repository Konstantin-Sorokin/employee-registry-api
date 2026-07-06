from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_helper
from app.repositories import EmployeeRepository
from app.services import EmployeeService


def get_employee_repo(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> EmployeeRepository:
    """Фабричная функция для получения репозитория сотрудников.

    Используется как зависимость FastAPI. Инжектит асинхронную сессию БД.
    """
    return EmployeeRepository(session=session)


def get_employee_service(
    repo: Annotated[EmployeeRepository, Depends(get_employee_repo)],
) -> EmployeeService:
    """Фабричная функция для получения сервиса сотрудников.

    Используется как зависимость FastAPI. Инжектит репозиторий сотрудников.
    """
    return EmployeeService(repo=repo)
