def require_activity_id(value: object) -> int:
    """Return a valid activity identifier or raise a domain validation error."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Activity ID must be an integer.")
    if value <= 0:
        raise ValueError("Activity ID must be a positive integer.")
    return value
