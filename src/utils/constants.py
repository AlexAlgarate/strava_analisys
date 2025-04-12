from typing import Dict

ACTIVITY_DETAILED_KEYS = [
    "name",
    "distance",
    "moving_time",
    "elapsed_time",
    "start_date_local",
    "gear_id",
    "average_heartrate",
    "max_heartrate",
    "calories",
    "perceived_exertion",
    "average_speed",
    "gear",
    "sport_type",
]

ACTIVITY_STREAMS_KEYS = [
    "time",
    "distance",
    "heartrate",
]


EXAMPLE_ID_ONE_ACTIVITY = 13200148363

EXAMPLE_ID_ACTIVITIES = [
    13200148363,
    13181274603,
    13229661332,
    13200144518,
    13150752938,
]

URL_GET_ACCESS_TOKEN = "https://www.strava.com/oauth/token"
OAUTH_URL = "https://www.strava.com/oauth/authorize"


MENU_DESCRIPTIONS: Dict[str, str] = {
    "ONE_ACTIVITY": "Show information for a specific activity",
    "LAST_200_ACTIVITIES": "Show information for activities the last 200 activities",
    "ACTIVITY_DETAILS": "Show detailed information for activities from current week",
    "ACTIVITY_DETAILS_PREV_WEEK": "Show detailed information for activities from previous week",
    "ACTIVITY_RANGE": "Show information for activities from current week",
    "ACTIVITY_RANGE_PREV_WEEK": "Show information for activities from last week",
    "SINGLE_STREAM": "Show the streams for ONE activity",
    "MULTIPLE_STREAMS": "Show the streams for MULTIPLE activities",
}
