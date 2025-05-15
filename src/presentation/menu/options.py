from enum import Enum, auto
from typing import Dict

MENU_DESCRIPTIONS: Dict[str, str] = {
    "ACTIVITY_DETAILS": "Show detailed information for activities from current week",
    "ACTIVITY_DETAILS_PREV_WEEK": "Show detailed information for activities from previous week",
    "ACTIVITY_RANGE": "Show all the information for activities from current week",
    "ACTIVITY_RANGE_PREV_WEEK": "Show all the information for activities from last week",
    "SINGLE_STREAM": "Show the streams for a specific activity",
    "MULTIPLE_STREAMS": "Show the streams for MULTIPLE activities",
    "STREAMS_CURRENT_WEEK": "Show the streams for the current week",
    "STREAMS_PREV_WEEK": "Show the streams for the previous week",
}


class MenuOption(Enum):
    ACTIVITY_DETAILS = auto()
    ACTIVITY_DETAILS_PREV_WEEK = auto()
    ACTIVITY_RANGE = auto()
    ACTIVITY_RANGE_PREV_WEEK = auto()
    SINGLE_STREAM = auto()
    MULTIPLE_STREAMS = auto()
    STREAMS_CURRENT_WEEK = auto()
    STREAMS_PREV_WEEK = auto()

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
