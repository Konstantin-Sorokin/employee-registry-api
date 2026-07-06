from datetime import date
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import urlencode

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.config import TEMPLATES_DIR, settings
from app.dependencies.employees import get_employee_service
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.schemas.filters import EmployeeFilter
from app.services.employee import EmployeeService
from app.utils.phone import normalize_phone
from app.utils.template_helpers import api_photo_url, format_phone_display, get_age

router = APIRouter(prefix=settings.api.employees_prefix)

templates = Jinja2Templates(directory=TEMPLATES_DIR)

templates.env.globals["get_age"] = get_age
templates.env.globals["format_phone_display"] = format_phone_display
templates.env.globals["api_photo_url"] = api_photo_url


@router.get("/")
async def list_page(
    request: Request,
    filters: Annotated[EmployeeFilter, Depends()],
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    page: int = Query(1, ge=1),
):
    """Отображает страницу со списком сотрудников.

    Поддерживает фильтрацию, поиск и пагинацию.
    При поиске по телефону нормализует номер перед запросом.

    Args:
        request: Объект HTTP-запроса FastAPI.
        filters: Параметры фильтрации (search, phone, gender, age_from, age_to).
        service: Экземпляр EmployeeService для бизнес-логики.
        page: Номер страницы (начиная с 1).

    Returns:
        TemplateResponse: HTML-страница со списком сотрудников.
    """
    phone_error = None
    if filters.phone:
        try:
            filters.phone = normalize_phone(filters.phone)
        except ValueError as e:
            phone_error = str(e)
            filters.phone = None

    result = await service.get_employees(filters=filters, page=page, limit=10)

    query_params = urlencode(filters.model_dump(exclude_none=True))

    return templates.TemplateResponse(
        request,
        "employees/list.html",
        {
            "employees": result.items,
            "page": result.page,
            "pages": result.pages,
            "filters": filters.model_dump(),
            "query_params": query_params,
            "phone_error": phone_error,
        },
    )


@router.get("/create")
async def create_page(request: Request):
    """Отображает форму для добавления нового сотрудника.

    Args:
        request: Объект HTTP-запроса FastAPI.

    Returns:
        TemplateResponse: HTML-страница с формой создания.
    """
    return templates.TemplateResponse(
        request,
        "employees/form.html",
        {
            "form_title": "Добавить сотрудника",
            "form_action": "/employees/create",
            "emp": None,
        },
    )


@router.post("/create")
async def create_employee(
    request: Request,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: Optional[str] = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    """Обрабатывает отправку формы создания сотрудника.

    Нормализует телефон, валидирует данные, создаёт запись в БД
    и сохраняет загруженную фотографию.

    Args:
        request: Объект HTTP-запроса FastAPI.
        service: Экземпляр EmployeeService.
        first_name: Имя сотрудника.
        last_name: Фамилия сотрудника.
        middle_name: Отчество (опционально).
        birth_date: Дата рождения в формате ISO (YYYY-MM-DD).
        gender: Пол ("Male" или "Female").
        phone: Номер телефона (опционально).
        photo: Загружаемый файл фотографии (опционально).

    Returns:
        RedirectResponse: Редирект на список сотрудников при успехе.
        TemplateResponse: Форма с ошибкой при неудаче.
    """
    try:
        normalized_phone = normalize_phone(phone)
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "employees/form.html",
            {
                "form_title": "Добавить сотрудника",
                "form_action": "/employees/create",
                "emp": None,
                "error": str(e),
            },
            status_code=400,
        )

    data = EmployeeCreate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_date=date.fromisoformat(birth_date),
        gender=gender,
        phone=normalized_phone,
    )

    try:
        await service.create_employee(data=data, photo=photo)
    except HTTPException as e:
        return templates.TemplateResponse(
            request,
            "employees/form.html",
            {
                "form_title": "Добавить сотрудника",
                "form_action": "/employees/create",
                "emp": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "middle_name": middle_name,
                    "birth_date": birth_date,
                    "gender": gender,
                    "phone": phone,
                },
                "error": e.detail,
            },
            status_code=e.status_code,
        )

    return RedirectResponse(url=settings.api.employees_prefix, status_code=303)


@router.get("/{employee_id}/edit")
async def edit_page(
    request: Request,
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    """Отображает форму редактирования сотрудника.

    Args:
        request: Объект HTTP-запроса FastAPI.
        employee_id: Идентификатор сотрудника.
        service: Экземпляр EmployeeService.

    Returns:
        TemplateResponse: HTML-страница с формой редактирования.

    Raises:
        HTTPException: 404, если сотрудник не найден.
    """
    try:
        emp = await service.get_employee_by_id(employee_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return templates.TemplateResponse(
        request,
        "employees/form.html",
        {
            "form_title": "Редактировать сотрудника",
            "form_action": f"/employees/{employee_id}",
            "emp": emp,
        },
    )


@router.post("/{employee_id}")
async def update_employee(
    request: Request,
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: Optional[str] = Form(None),
    birth_date: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    """Обрабатывает обновление данных сотрудника.

    Нормализует телефон, валидирует данные и обновляет запись в БД.
    При загрузке нового фото удаляет старое.

    Args:
        request: Объект HTTP-запроса FastAPI.
        employee_id: Идентификатор сотрудника.
        service: Экземпляр EmployeeService.
        first_name: Имя сотрудника.
        last_name: Фамилия сотрудника.
        middle_name: Отчество (опционально).
        birth_date: Дата рождения в формате ISO (YYYY-MM-DD).
        gender: Пол ("Male" или "Female").
        phone: Номер телефона (опционально).
        photo: Загружаемый файл фотографии (опционально).

    Returns:
        RedirectResponse: Редирект на список сотрудников при успехе.
        TemplateResponse: Форма с ошибкой при неудаче.

    Raises:
        HTTPException: 404, если сотрудник не найден.
    """
    try:
        current_emp = await service.get_employee_by_id(employee_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    try:
        normalized_phone = normalize_phone(phone)
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "employees/form.html",
            {
                "form_title": "Редактировать сотрудника",
                "form_action": f"/employees/{employee_id}",
                "emp": current_emp,
                "error": str(e),
            },
            status_code=400,
        )

    data = EmployeeUpdate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_date=date.fromisoformat(birth_date),
        gender=gender,
        phone=normalized_phone,
    )

    try:
        await service.update_employee(employee_id=employee_id, data=data, photo=photo)
    except HTTPException as e:
        return templates.TemplateResponse(
            request,
            "employees/form.html",
            {
                "form_title": "Редактировать сотрудника",
                "form_action": f"/employees/{employee_id}",
                "emp": current_emp,
                "error": e.detail,
            },
            status_code=e.status_code,
        )

    return RedirectResponse(url=settings.api.employees_prefix, status_code=303)


@router.post("/{employee_id}/delete")
async def delete_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    """Удаляет сотрудника и его фотографию (если есть).

    Args:
        employee_id: Идентификатор сотрудника.
        service: Экземпляр EmployeeService.

    Returns:
        RedirectResponse: Редирект на список сотрудников.

    Raises:
        HTTPException: 404, если сотрудник не найден.
    """
    try:
        await service.delete_employee(employee_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return RedirectResponse(url=settings.api.employees_prefix, status_code=303)
