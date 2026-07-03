from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.core import settings
from app.dependencies.employees import get_employee_service
from app.schemas import (
    EmployeeCreate,
    EmployeeFilter,
    EmployeeResponse,
    EmployeeUpdate,
    PaginationResponse,
)
from app.services import EmployeeService

router = APIRouter(prefix=settings.api.employees_prefix, tags=["Сотрудники"])


@router.get("", response_model=PaginationResponse[EmployeeResponse])
async def get_employees(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество на странице"),
    phone: Optional[str] = Query(None, description="Номер телефона"),
    search: Optional[str] = Query(None, description="Поиск по ФИО"),
    gender: Optional[str] = Query(None, description="Пол сотрудника"),
    age_from: Optional[int] = Query(None, ge=0, le=150, description="Возраст от"),
    age_to: Optional[int] = Query(None, ge=0, le=150, description="Возраст до"),
):
    filters = EmployeeFilter(
        phone=phone,
        search=search,
        gender=gender,
        age_from=age_from,
        age_to=age_to,
    )
    return await service.get_employees(filters=filters, page=page, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    return await service.get_employee_by_id(employee_id)


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    first_name: str = Form(..., min_length=1, max_length=100),
    last_name: str = Form(..., min_length=1, max_length=100),
    middle_name: Optional[str] = Form(None, min_length=1, max_length=100),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    data = EmployeeCreate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone=phone,
    )
    return await service.create_employee(data=data, photo=photo)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    first_name: Optional[str] = Form(None, min_length=1, max_length=100),
    last_name: Optional[str] = Form(None, min_length=1, max_length=100),
    middle_name: Optional[str] = Form(None, min_length=1, max_length=100),
    birth_date: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    data = EmployeeUpdate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone=phone,
    )
    return await service.update_employee(
        employee_id=employee_id, data=data, photo=photo
    )


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    return await service.delete_employee(employee_id)
