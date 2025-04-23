from enum import Enum
from typing import Dict


class ActivityDetailKey(Enum):
    NAME = "name"
    DISTANCE = "distance"
    MOVING_TIME = "moving_time"
    ELAPSED_TIME = "elapsed_time"
    START_DATE_LOCAL = "start_date_local"
    GEAR_ID = "gear_id"
    AVERAGE_HEARTRATE = "average_heartrate"
    MAX_HEARTRATE = "max_heartrate"
    CALORIES = "calories"
    PERCEIVED_EXERTION = "perceived_exertion"
    AVERAGE_SPEED = "average_speed"
    SPORT_TYPE = "sport_type"
    GEAR = "gear"


ACTIVITY_STREAMS_KEYS = [
    "time",
    "distance",
    "heartrate",
]


EXAMPLE_ID_ONE_ACTIVITY = 14245158296

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
    "CURRENT_WEEK_REPORT": "Show the weekly report for the current week",
    "LAST_WEEK_REPORT": "Show the weekly report for the last week",
}
