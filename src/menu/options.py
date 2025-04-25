from enum import Enum, auto
from typing import Dict

MENU_DESCRIPTIONS: Dict[str, str] = {
    "ONE_ACTIVITY": "Show information for a specific activity",
    "LAST_200_ACTIVITIES": "Show information for activities the last 200 activities",
    "ACTIVITY_DETAILS": "Show detailed information for activities from current week",
    "ACTIVITY_DETAILS_PREV_WEEK": "Show detailed information for activities from previous week",
    "ACTIVITY_RANGE": "Show all the information for activities from current week",
    "ACTIVITY_RANGE_PREV_WEEK": "Show all the information for activities from last week",
    "SINGLE_STREAM": "Show the streams for a specific activity",
    "MULTIPLE_STREAMS": "Show the streams for MULTIPLE activities",
    "CURRENT_WEEK_REPORT": "Show the weekly report for the current week",
    "LAST_WEEK_REPORT": "Show the weekly report for the last week",
}


class MenuOption(Enum):
    ONE_ACTIVITY = auto()
    LAST_200_ACTIVITIES = auto()
    ACTIVITY_DETAILS = auto()
    ACTIVITY_DETAILS_PREV_WEEK = auto()
    ACTIVITY_RANGE = auto()
    ACTIVITY_RANGE_PREV_WEEK = auto()
    SINGLE_STREAM = auto()
    MULTIPLE_STREAMS = auto()
    CURRENT_WEEK_REPORT = auto()
    LAST_WEEK_REPORT = auto()

    @property
    def id(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return MENU_DESCRIPTIONS[self.name]

    @classmethod
    def validate_descriptions(cls) -> None:
        missing = [
            member.name for member in cls if member.name not in MENU_DESCRIPTIONS
        ]
        if missing:
            raise ValueError(
                f"Missing descriptions for menu options: {', '.join(missing)}"
            )


MenuOption.validate_descriptions()
