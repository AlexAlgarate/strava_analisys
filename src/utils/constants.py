ACTIVITY_DETAILED_KEYS = [
    "name",
    "distance",
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
print_options_main = {
    "1": "Show information for a specific activity",
    "2": "Show detailed information for a specific activity",
    "3": "Show the last 200 activities",
    "4": "Show information for activities from the current week",
    "5": "Show information for activities from the previous week",
    "6": "Show streams for activities from the current week",
    "7": "Show a graph of time in zone for a specific activity",
    "8": "Exit",
}
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
