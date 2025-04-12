from enum import Enum, auto

from src.utils.constants import MENU_DESCRIPTIONS


class MenuOption(Enum):
    """Enum representing menu options with their descriptions"""

    ONE_ACTIVITY = auto()
    LAST_200_ACTIVITIES = auto()
    ACTIVITY_DETAILS = auto()
    ACTIVITY_DETAILS_PREV_WEEK = auto()
    ACTIVITY_RANGE = auto()
    ACTIVITY_RANGE_PREV_WEEK = auto()
    SINGLE_STREAM = auto()
    MULTIPLE_STREAMS = auto()

    @property
    def id(self) -> int:
        return self.value

    @property
    def description(self) -> str:
        return MENU_DESCRIPTIONS[self.name]

    @classmethod
    def validate_descriptions(cls) -> None:
        """Validates that all enum members have corresponding descriptions"""
        missing = [
            member.name for member in cls if member.name not in MENU_DESCRIPTIONS
        ]
        if missing:
            raise ValueError(
                f"Missing descriptions for menu options: {', '.join(missing)}"
            )


MenuOption.validate_descriptions()
