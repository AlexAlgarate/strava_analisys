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
]

ACTIVITY_STREAMS_KEYS = [
    "time",
    "distance",
    "heartrate",
]

PRINT_OPTIONS = {
    "1": "Show information for a specific activity",
    "2": "Show detailed information for activities from current week",
    "3": "Show detailed information for activities from previous week",
    "4": "Show information for activities the last 200 activities",
    "5": "Show information for activities from current week",
    "6": "Show information for activities from last week",
    # "7": "Show the streams from the current week",
    # "8": "Show the streams from the previous week",
}

EXIT_OPTION = "exit"

EXAMPLE_ID_ACTIVITIES = [
    13200148363,
    13181274603,
    13229661332,
    13200144518,
    13150752938,
]

STRAVA_API_ACTIVITIES = "https://www.strava.com/api/v3/activities"
URL_GET_ACCESS_TOKEN = "https://www.strava.com/oauth/token"
OAUTH_URL = "https://www.strava.com/oauth/authorize"
