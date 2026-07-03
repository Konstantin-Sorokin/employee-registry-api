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
        if isinstance(v, str):
            return v.strip()
        return v
