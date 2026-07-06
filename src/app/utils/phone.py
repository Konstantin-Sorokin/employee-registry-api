from typing import Optional


def normalize_phone(phone: str) -> Optional[str]:
    """Нормализует номер телефона.

    Из 10 цифр делает 11 с префиксом 7. Если передано 11 цифр — возвращает как есть.

    Args:
        phone: Строка с номером телефона (может содержать +, (, ), -, пробелы).

    Returns:
        Optional[str]: Строка из 11 цифр или None, если phone пустой.

    Raises:
        ValueError: Если цифр меньше 10 или больше 11.
    """
    if not phone:
        return None

    digits = "".join(c for c in phone if c.isdigit())

    if len(digits) == 10:
        return "7" + digits
    if len(digits) == 11:
        return digits

    raise ValueError("Номер телефона должен содержать 10 цифр после +7")
