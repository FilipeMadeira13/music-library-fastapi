def validate_name(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError('The name field cannot be empty.')
    return v