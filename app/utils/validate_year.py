from datetime import datetime
from typing import Optional


def validate_year(v: Optional[int]) -> Optional[int]:
    if v is not None and v > datetime.now().year:
        raise ValueError("O ano de formação não pode ser no futuro")
    return v