from datetime import date
from typing import Optional


def get_age(birth_date: Optional[date]) -> int:
    """Вычисляет возраст на основе даты рождения.

    Args:
        birth_date: Дата рождения или None.

    Returns:
        int: Возраст в годах. 0, если дата не указана.
    """
    if not birth_date:
        return 0
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def format_phone_display(phone: Optional[str]) -> str:
    """Форматирует номер телефона в читаемый вид: +7 (XXX) XXX-XX-XX.

    Args:
        phone: Строка с номером телефона или None.

    Returns:
        str: Отформатированный номер или '—' если номер пустой.
    """
    if not phone:
        return "—"
    clean = "".join(c for c in phone if c.isdigit())
    if len(clean) != 11:
        return phone
    d = clean[1:]
    return f"+7 ({d[:3]}) {d[3:6]}-{d[6:8]}-{d[8:10]}"


def api_photo_url(filename: Optional[str]) -> str:
    """Формирует URL для доступа к фотографии сотрудника.

    Args:
        filename: Имя файла фотографии или None.

    Returns:
        str: URL-путь к фото или путь к заглушке, если файл не указан.
    """
    if not filename:
        return "/static/placeholder.svg"
    return f"/uploads/photos/{filename}"
