from typing import Literal, Optional

from pydantic import BaseModel


class EmployeeFilter(BaseModel):
    search: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[Literal["Male", "Female"]] = None
    age_from: Optional[int] = None
    age_to: Optional[int] = None
