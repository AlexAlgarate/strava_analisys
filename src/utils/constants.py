from enum import Enum


class ActivityDetailKey(Enum):
    NAME = "name"
    DISTANCE = "distance"
    ID_ACTIVITY = "id"
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
