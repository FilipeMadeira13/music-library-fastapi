from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.utils.validate_year import validate_year


class Artist(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    formation_year: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    validate_formation_year = field_validator("formation_year")(
        validate_year
    )


class ArtistCreateUpdate(BaseModel):
    name: str
    country: Optional[str] = None
    formation_year: Optional[int] = None

    validate_formation_year = field_validator("formation_year")(
        validate_year
    )
