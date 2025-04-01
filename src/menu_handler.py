import asyncio
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict

from src.strava_service import StravaService
from src.utils import constants as constant


class MenuOption(Enum):
    ONE_ACTIVITY = auto()
    LAST_200_ACTIVITIES = auto()
    ACTIVITY_DETAILS = auto()
    ACTIVITY_DETAILS_PREV_WEEK = auto()
    ACTIVITY_RANGE = auto()
    ACTIVITY_RANGE_PREV_WEEK = auto()
    SINGLE_STREAM = auto()
    MULTIPLE_STREAMS = auto()


@dataclass
class MenuDescription:
    option: MenuOption
    description: str
    handler: Callable[[], Any]


class MenuHandler:
    def __init__(self, service: StravaService):
        self.service = service

        self.menu_options: Dict[MenuOption, MenuDescription] = {
            MenuOption.ONE_ACTIVITY: lambda: self.service.get_one_activity(
                activity_id=13654451097
            ),
            MenuOption.LAST_200_ACTIVITIES: self.service.get_last_200_activities,
            MenuOption.ACTIVITY_DETAILS: lambda: asyncio.run(
                self.service.get_activity_details(previous_week=False)
            ),
            MenuOption.ACTIVITY_DETAILS_PREV_WEEK: lambda: asyncio.run(
                self.service.get_activity_details(previous_week=True)
            ),
            MenuOption.ACTIVITY_RANGE: lambda: asyncio.run(
                self.service.get_activity_range(previous_week=False)
            ),
            MenuOption.ACTIVITY_RANGE_PREV_WEEK: lambda: asyncio.run(
                self.service.get_activity_range(previous_week=True)
            ),
            MenuOption.SINGLE_STREAM: lambda: asyncio.run(
                self.service.get_streams_for_activity(activity_id=13654451097)
            ),
            MenuOption.MULTIPLE_STREAMS: lambda: asyncio.run(
                self.service.get_streams_for_multiple_activities(
                    activity_ids=constant.EXAMPLE_ID_ACTIVITIES
                )
            ),
        }

    def get_menu_options(self) -> Dict[str, str]:
        return {
            str(option.value): option.name.replace("_", " ").title()
            for option in MenuOption
        }

    def execute_option(self, option: str) -> Any:
        try:
            menu_option = MenuOption(int(option))
            result = self.menu_options[menu_option]()
            print(result)
            return result
        except (ValueError, KeyError):
            print(f"❌ Invalid option: {option}\n")
            return None

    def print_menu(self) -> None:
        print("\n📌 Choose an option:\n")
        for key, desc in self.get_menu_options().items():
            print(f"{key}. {desc}")
