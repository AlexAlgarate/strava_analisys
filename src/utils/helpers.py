from datetime import UTC, datetime, timedelta


def get_week_epoch_range(previous_week: bool = False) -> tuple[int, int]:
    """Get epoch timestamp range for current or previous week."""
    now = datetime.now(UTC)
    current_weekday = now.weekday()
    monday = now - timedelta(days=current_weekday)

    if previous_week:
        monday = monday - timedelta(weeks=1)

    # Reset to start of Monday (00:00:00)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=7)

    return int(monday.timestamp()), int(sunday.timestamp())
