from datetime import datetime
from typing import Optional


def validate_year(v: Optional[int]) -> Optional[int]:
    if v is not None and v > datetime.now().year:
        raise ValueError("The year cannot be in the future.")
    return v
