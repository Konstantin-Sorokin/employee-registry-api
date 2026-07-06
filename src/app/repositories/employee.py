from datetime import date, timedelta

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Employee
from app.schemas import EmployeeFilter


class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, employee_id: int) -> Employee | None:
        """Получает сотрудника по первичному ключу."""
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Employee:
        """Создаёт нового сотрудника в БД.

        Args:
            data: Словарь с данными сотрудника.
        """
        employee = Employee(**data)
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        return employee

    async def update(self, employee: Employee, data: dict) -> Employee:
        """Обновляет поля существующего сотрудника.

        Args:
            employee: Объект сотрудника для обновления.
            data: Словарь с обновлёнными данными.
        """
        if not data:
            return employee
        for key, value in data.items():
            setattr(employee, key, value)
        await self.session.commit()
        await self.session.refresh(employee)
        return employee

    async def delete(self, employee: Employee) -> None:
        """Удаляет сотрудника из БД."""
        await self.session.delete(employee)
        await self.session.commit()

    async def get_filtered_employees(
        self, filters: EmployeeFilter, skip: int = 0, limit: int = 100
    ) -> list[Employee]:
        """Получает список сотрудников с фильтрацией и пагинацией.

        Args:
            filters: Критерии фильтрации.
            skip: Количество пропускаемых записей (смещение).
            limit: Максимальное количество записей.
        """
        stmt = self._build_filter_query(filters)
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered_employees(self, filters: EmployeeFilter) -> int:
        """Считает общее количество сотрудников, удовлетворяющих фильтрам."""
        base_stmt = self._build_filter_query(filters)
        count_stmt = select(func.count()).select_from(base_stmt.subquery())

        result = await self.session.execute(count_stmt)
        return result.scalar_one()

    def _years_ago(self, today: date, years: int) -> date:
        """Безопасный расчёт даты N лет назад (учитывает 29 февраля).

        Args:
            today: Текущая дата.
            years: Количество лет.

        Returns:
            date: Дата N лет назад.
        """
        try:
            return today.replace(year=today.year - years)
        except ValueError:
            return today.replace(year=today.year - years, day=28)

    def _build_filter_query(self, filters: EmployeeFilter) -> Select[tuple[Employee]]:
        """Строит SQL-запрос с учётом всех условий фильтрации.

        Поддерживает поиск по телефону (приоритет 1) и умный поиск по ФИО
        с разбивкой поискового запроса на слова, а также фильтрацию по полу и возрасту.
        """
        stmt = select(Employee).order_by(Employee.id)
        conditions = []

        # --- ПРИОРИТЕТ 1: Поиск по телефону ---
        if filters.phone:
            conditions.append(Employee.phone == filters.phone)

        # --- ПРИОРИТЕТ 2: Умный поиск по ФИО + Фильтры ---
        else:
            if filters.search:
                search_terms = filters.search.strip().split()
                term_conditions = []

                for term in search_terms:
                    if term:
                        word_filter = or_(
                            Employee.first_name.ilike(f"%{term}%"),
                            Employee.last_name.ilike(f"%{term}%"),
                            Employee.middle_name.ilike(f"%{term}%"),
                        )
                        term_conditions.append(word_filter)

                if term_conditions:
                    conditions.append(and_(*term_conditions))

            if filters.gender:
                conditions.append(Employee.gender == filters.gender)

            today = date.today()
            if filters.age_from is not None:
                max_bd = self._years_ago(today, filters.age_from)
                conditions.append(Employee.birth_date <= max_bd)

            if filters.age_to is not None:
                min_bd = self._years_ago(today, filters.age_to + 1) + timedelta(days=1)
                conditions.append(Employee.birth_date >= min_bd)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        return stmt
