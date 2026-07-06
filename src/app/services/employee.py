from typing import Optional

from fastapi import HTTPException, UploadFile

from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.schemas.filters import EmployeeFilter
from app.schemas.pagination import PaginationResponse
from app.utils.files import delete_photo, process_and_save_photo


class EmployeeService:
    def __init__(self, repo: EmployeeRepository):
        self.repo = repo

    async def _get_employee_or_404(self, employee_id: int):
        """Получает сотрудника по ID или выбрасывает 404.

        Args:
            employee_id: Идентификатор сотрудника.

        Returns:
            Employee: Объект модели сотрудника.

        Raises:
            HTTPException: 404, если сотрудник не найден.
        """
        employee = await self.repo.get_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")
        return employee

    async def get_employees(
        self, filters: EmployeeFilter, page: int = 1, limit: int = 10
    ) -> PaginationResponse[EmployeeResponse]:
        """Получает список сотрудников с фильтрацией и пагинацией.

        Args:
            filters: Критерии фильтрации (поиск, телефон, пол, возраст).
            page: Номер страницы (начиная с 1, по умолчанию 1).
            limit: Количество записей на странице (по умолчанию 10).

        Returns:
            PaginationResponse[EmployeeResponse]: Результаты с метаданными пагинации.
        """
        skip = (page - 1) * limit
        employees = await self.repo.get_filtered_employees(
            filters=filters, skip=skip, limit=limit
        )
        total = await self.repo.count_filtered_employees(filters=filters)

        items = [EmployeeResponse.model_validate(emp) for emp in employees]
        pages = (total + limit - 1) // limit if total > 0 else 0

        return PaginationResponse(
            items=items, total=total, page=page, limit=limit, pages=pages
        )

    async def get_employee_by_id(self, employee_id: int) -> EmployeeResponse:
        """Получает данные сотрудника по ID."""
        employee = await self._get_employee_or_404(employee_id)
        return EmployeeResponse.model_validate(employee)

    async def create_employee(
        self, data: EmployeeCreate, photo: Optional[UploadFile] = None
    ) -> EmployeeResponse:
        """Создаёт нового сотрудника.

        При наличии фотографии обрабатывает и сохраняет её.

        Args:
            data: Данные нового сотрудника.
            photo: Файл фотографии (опционально).

        Returns:
            EmployeeResponse: Созданный сотрудник.
        """
        employee_data = data.model_dump()

        photo_filename = None
        if photo and photo.filename:
            photo_filename = await process_and_save_photo(photo)
            employee_data["photo_filename"] = photo_filename

        new_employee = await self.repo.create(employee_data)
        return EmployeeResponse.model_validate(new_employee)

    async def update_employee(
        self, employee_id: int, data: EmployeeUpdate, photo: Optional[UploadFile] = None
    ) -> EmployeeResponse:
        """Обновляет данные сотрудника.

        При загрузке новой фотографии удаляет старую.

        Args:
            employee_id: Идентификатор сотрудника.
            data: Обновлённые данные (только переданные поля).
            photo: Новый файл фотографии (опционально).

        Returns:
            EmployeeResponse: Обновлённый сотрудник.
        """
        employee = await self._get_employee_or_404(employee_id)

        photo_filename = None
        if photo and photo.filename:
            photo_filename = await process_and_save_photo(photo)

        update_data = data.model_dump(exclude_unset=True)

        if photo_filename:
            if employee.photo_filename:
                delete_photo(employee.photo_filename)
            update_data["photo_filename"] = photo_filename

        if update_data:
            updated_employee = await self.repo.update(employee, update_data)
            return EmployeeResponse.model_validate(updated_employee)

        return EmployeeResponse.model_validate(employee)

    async def delete_employee(self, employee_id: int) -> dict:
        """Удаляет сотрудника и его фотографию (если есть).

        Args:
            employee_id: Идентификатор сотрудника.

        Returns:
            dict: Сообщение об успешном удалении.
        """
        employee = await self._get_employee_or_404(employee_id)
        if employee.photo_filename:
            delete_photo(employee.photo_filename)
        await self.repo.delete(employee)
        return {"detail": "Сотрудник успешно удален"}
