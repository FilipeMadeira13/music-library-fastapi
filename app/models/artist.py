from datetime import date
from typing import Optional

from pydantic import BaseModel


class Artist(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    formed_in: Optional[date] = None
