from typing import Any

import pytest

from src.core.activities.utils import get_activity_ids


class TestActivityUtils:
    @pytest.mark.asyncio
    async def test_get_activity_ids_empty_list(self) -> None:
        result = await get_activity_ids([])
        assert result == []

    @pytest.mark.asyncio
    async def test_get_activity_ids_multiple_activities(self) -> None:
        activities = [
            {"id": 1, "name": "Activity 1"},
            {"id": 2, "name": "Activity 2"},
            {"id": 3, "name": "Activity 3"},
        ]
        result = await get_activity_ids(activities)
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_get_activity_ids_with_missing_ids(self) -> None:
        activities: list[dict[str, Any]] = [{"name": "Activity 1"}, {"id": 2}]
        with pytest.raises(KeyError):
            await get_activity_ids(activities)
