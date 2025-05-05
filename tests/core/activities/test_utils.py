import pytest

from src.core.activities.utils import get_activity_ids


class TestActivityUtils:
    @pytest.mark.asyncio
    async def test_get_activity_ids_empty_list(self):
        result = await get_activity_ids([])
        assert result == []

    @pytest.mark.asyncio
    async def test_get_activity_ids_multiple_activities(self):
        activities = [
            {"id": 1, "name": "Activity 1"},
            {"id": 2, "name": "Activity 2"},
            {"id": 3, "name": "Activity 3"},
        ]
        result = await get_activity_ids(activities)
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_get_activity_ids_with_missing_ids(self):
        activities = [{"name": "Activity 1"}, {"id": 2}]
        with pytest.raises(KeyError):
            await get_activity_ids(activities)
