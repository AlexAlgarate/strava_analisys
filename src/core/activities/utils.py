from typing import Dict, List


async def get_activity_ids(activities: List[Dict]) -> List[int]:
    """Extract activity IDs from a list of activity dictionaries.

    Args:
        activities: List of activity dictionaries from Strava API

    Returns:
        List of activity IDs
    """
    return [activity["id"] for activity in activities]
