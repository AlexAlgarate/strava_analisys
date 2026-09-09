from enum import Enum, StrEnum


class MenuCategory(StrEnum):
    ACTIVITIES = "Activities"
    STREAMS = "Streams & exports"
    INSIGHTS = "Insights"


class MenuOption(Enum):
    ACTIVITY_DETAILS = (
        1,
        MenuCategory.ACTIVITIES,
        "Detailed activities · current week",
    )
    ACTIVITY_DETAILS_PREV_WEEK = (
        2,
        MenuCategory.ACTIVITIES,
        "Detailed activities · previous week",
    )
    ACTIVITY_RANGE = (3, MenuCategory.ACTIVITIES, "Activity list · current week")
    ACTIVITY_RANGE_PREV_WEEK = (
        4,
        MenuCategory.ACTIVITIES,
        "Activity list · previous week",
    )
    SINGLE_STREAM = (5, MenuCategory.STREAMS, "View one activity stream")
    MULTIPLE_STREAMS = (6, MenuCategory.STREAMS, "View several activity streams")
    STREAMS_CURRENT_WEEK = (
        7,
        MenuCategory.STREAMS,
        "Export current-week streams to CSV",
    )
    STREAMS_PREV_WEEK = (
        8,
        MenuCategory.STREAMS,
        "Export previous-week streams to CSV",
    )
    WEEKLY_REPORT = (9, MenuCategory.INSIGHTS, "Weekly training summary")
    ACTIVITY_ZONES = (10, MenuCategory.INSIGHTS, "View heart-rate zones")

    def __init__(
        self,
        option_id: int,
        category: MenuCategory,
        description: str,
    ) -> None:
        self._option_id = option_id
        self._category = category
        self._description = description

    @property
    def id(self) -> int:
        return self._option_id

    @property
    def category(self) -> MenuCategory:
        return self._category

    @property
    def description(self) -> str:
        return self._description
