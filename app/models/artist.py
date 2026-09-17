from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


def validate_formation_year(v: Optional[int]) -> Optional[int]:
    if v is not None and v > datetime.now().year:
        raise ValueError("O ano de formação não pode ser no futuro")
    return v


class Artist(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    formation_year: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    _validate_formation_year = field_validator("formation_year")(
        validate_formation_year
    )


class ArtistCreateUpdate(BaseModel):
    name: str
    country: Optional[str] = None
    formation_year: Optional[int] = None

    _validate_formation_year = field_validator("formation_year")(
        validate_formation_year
    )
