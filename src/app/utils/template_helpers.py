from datetime import date
from typing import Optional


def get_age(birth_date: Optional[date]) -> int:
    if not birth_date:
        return 0
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def format_phone_display(phone: Optional[str]) -> str:
    if not phone:
        return "—"
    clean = "".join(c for c in phone if c.isdigit())
    if len(clean) != 11:
        return phone
    d = clean[1:]
    return f"+7 ({d[:3]}) {d[3:6]}-{d[6:8]}-{d[8:10]}"


def api_photo_url(filename: Optional[str]) -> str:
    if not filename:
        return "/static/placeholder.svg"
    return f"/uploads/photos/{filename}"
