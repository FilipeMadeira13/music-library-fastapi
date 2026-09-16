from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field

class Artist(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    formed_in: Annotated[Optional[int], Field(le=datetime.now().year)]
