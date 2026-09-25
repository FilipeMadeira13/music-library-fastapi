from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.validate_name import validate_name
from app.utils.validate_year import validate_year


class Artist(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    formation_year: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    validate_formation_year = field_validator("formation_year")(validate_year)


class ArtistCreateUpdate(BaseModel):
    name: str = Field(min_length=1)
    country: Optional[str] = None
    formation_year: Optional[int] = None

    _validate_name = field_validator("name")(validate_name)
    validate_formation_year = field_validator("formation_year")(validate_year)
