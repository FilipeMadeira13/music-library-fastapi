from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.validate_year import validate_year


class Album(BaseModel):
    id: int
    title: str
    artist_id:int 
    release_year: Optional[int] = None
    genre: Optional[str] = None
    number_of_tracks: Optional[int] = Field(default=None, gt=0)
    created_at: datetime
    updated_at: datetime

    validate_release_year = field_validator("release_year")(
            validate_year
        )