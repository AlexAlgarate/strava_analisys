import pytest

from src.core.activities.utils import get_activity_ids


class TestActivityUtils:
    def test_get_activity_ids_empty_list(self) -> None:
        result = get_activity_ids([])
        assert result == []

    def test_get_activity_ids_multiple_activities(self) -> None:
        activities = [
            {"id": 1, "name": "Activity 1"},
            {"id": 2, "name": "Activity 2"},
            {"id": 3, "name": "Activity 3"},
        ]
        result = get_activity_ids(activities)
        assert result == [1, 2, 3]

    def test_get_activity_ids_with_missing_ids(self) -> None:
        activities: list[dict[str, object]] = [{"name": "Activity 1"}, {"id": 2}]
        with pytest.raises(TypeError, match="integer id"):
            get_activity_ids(activities)
