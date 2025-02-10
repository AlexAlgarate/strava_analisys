import logging
import time


class Logger:
    @staticmethod
    def setup_logger():
        """Configures and returns the logger."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger(__name__)


def setup_logger():
    """Configures and returns the logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def func_time_execution(func):
    async def wraper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"\nExecution time: {end - start:.2f} seconds\n")
        return result

    return wraper


base_url_oauth = "https://www.strava.com/oauth/authorize"


base_url_access_token = "https://www.strava.com/oauth/token"

activities_url = "https://www.strava.com/api/v3/activities"


activity_detailed_keys = [
    "name",
    "distance",
    "start_date_local",
    "gear_id",
    "average_heartrate",
    "max_heartrate",
    "calories",
    "perceived_exertion",
]

streams_keys = [
    "time",
    "distance",
    "heartrate",
]

id_activities = [13200148363, 13181274603, 13229661332, 13200144518, 13150752938]
