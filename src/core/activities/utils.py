from collections.abc import Mapping, Sequence


def get_activity_ids(activities: Sequence[Mapping[str, object]]) -> list[int]:
    """Extract activity IDs from a list of activity dictionaries.

    Args:
        activities: List of activity dictionaries from Strava API

    Returns:
        List of activity IDs
    """
    activity_ids: list[int] = []
    for activity in activities:
        activity_id = activity.get("id")
        if isinstance(activity_id, bool) or not isinstance(activity_id, int):
            raise TypeError("An activity must contain an integer id.")
        activity_ids.append(activity_id)
    return activity_ids
