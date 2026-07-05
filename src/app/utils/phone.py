from typing import Optional


def normalize_phone(phone: str) -> Optional[str]:
    """
    Преобразует 10 цифр в 11 с 7 в начале.
    Возвращает None, если телефон пустой.
    Вызывает ValueError, если цифр меньше 10.
    """
    if not phone:
        return None

    digits = "".join(c for c in phone if c.isdigit())

    if len(digits) == 10:
        return "7" + digits
    if len(digits) == 11:
        return digits

    raise ValueError("Номер телефона должен содержать 10 цифр после +7")
