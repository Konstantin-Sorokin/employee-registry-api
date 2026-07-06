from pydantic import BaseModel, ConfigDict, field_validator


class OrmMixin(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


class IdMixin(BaseModel):
    id: int


class NameStripMixin(BaseModel):
    @field_validator(
        "first_name", "last_name", "middle_name", mode="before", check_fields=False
    )
    @classmethod
    def strip_names(cls, v):
        """Обрезает пробелы в начале и конце строковых полей.

        Применяется к полям first_name, last_name, middle_name перед валидацией.

        Args:
            v: Значение поля.

        Returns:
            str: Обрезанная строка или исходное значение, если не строка.
        """
        if isinstance(v, str):
            return v.strip()
        return v
