from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column


class IdPkMixin:
    """Миксин для добавления первичного ключа id к моделям.

    Предоставляет стандартное поле id в качестве первичного ключа
    для моделей базы данных.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
