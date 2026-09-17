from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator

class Artist(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    formation_year: Optional[int] = None

    @field_validator('formation_year')
    @classmethod
    def check_formed_in(cls, v):
        if v is not None and v > datetime.now().year:
            raise ValueError("O ano de formação não pode ser no futuro")
        return v
