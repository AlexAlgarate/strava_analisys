from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.results import StreamExportResult
from src.application.use_cases.activities import ActivityService
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.application.use_cases.activity_zones import ActivityZonesService
from src.application.use_cases.activity_zones_export import ActivityZonesExportService
from src.application.use_cases.stream_export import StreamExportService
from src.application.use_cases.streams import ActivityStreamService
from src.composition import ApplicationServices, build_menu_commands
from src.domain.activity_stream import StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.week_period import WeekSelection
from src.presentation.menu.commands import MenuCommandRegistry
from src.presentation.menu.options import MenuOption
from src.presentation.ports import PromptReader, ResultPresenter, WeeklySummaryPresenter
from tests.factories import activity_model, activity_stream, heart_rate_zones


@dataclass(frozen=True, slots=True)
class CommandComposition:
    registry: MenuCommandRegistry
    services: ApplicationServices
    prompts: Mock
    result_presenter: Mock
    summary_presenter: Mock
    activities: Mock
    streams: Mock
    stream_export: Mock
    activity_zones: Mock
    summary: Mock


@pytest.fixture
def command_composition() -> CommandComposition:
    activities = Mock(spec=ActivityService)
    activities.get_activity_details = AsyncMock(return_value=[activity_model()])
    activities.get_activity_range = AsyncMock(return_value=[activity_model()])

    streams = Mock(spec=ActivityStreamService)
    streams.get_streams_for_activity = AsyncMock(return_value=activity_stream(123))
    streams.get_streams_for_multiple_activities = AsyncMock(
        return_value=StreamBatch(streams=(activity_stream(123),))
    )

    stream_export = Mock(spec=StreamExportService)
    stream_export.export_streams_for_selected_week = AsyncMock(
        return_value=StreamExportResult(StreamBatch(), Path("streams.csv"))
    )

    activity_zones = Mock(spec=ActivityZonesService)
    activity_zones.get_activity_zones = AsyncMock(return_value=heart_rate_zones(123))

    summary = Mock(spec=ActivitySummaryService)
    summary.generate_summary = AsyncMock(
        return_value=WeeklyActivitySummary.from_activities([])
    )

    services = ApplicationServices(
        activities=activities,
        streams=streams,
        stream_export=stream_export,
        activity_zones=activity_zones,
        activity_zones_export=Mock(spec=ActivityZonesExportService),
        summary=summary,
    )
    prompts = Mock(spec=PromptReader)
    prompts.ask_activity_id.return_value = 123
    prompts.ask_activity_ids.return_value = [123, 456]
    result_presenter = Mock(spec=ResultPresenter)
    summary_presenter = Mock(spec=WeeklySummaryPresenter)

    return CommandComposition(
        registry=build_menu_commands(
            services,
            prompts=prompts,
            result_presenter=result_presenter,
            summary_presenter=summary_presenter,
        ),
        services=services,
        prompts=prompts,
        result_presenter=result_presenter,
        summary_presenter=summary_presenter,
        activities=activities,
        streams=streams,
        stream_export=stream_export,
        activity_zones=activity_zones,
        summary=summary,
    )


def test_builds_the_complete_default_command_catalog(
    command_composition: CommandComposition,
) -> None:
    assert command_composition.registry.options == tuple(MenuOption)


@pytest.mark.parametrize(
    ("option", "method_name", "week", "presenter_name"),
    [
        (
            MenuOption.ACTIVITY_DETAILS,
            "get_activity_details",
            WeekSelection.CURRENT,
            "present_detailed_activities",
        ),
        (
            MenuOption.ACTIVITY_DETAILS_PREV_WEEK,
            "get_activity_details",
            WeekSelection.PREVIOUS,
            "present_detailed_activities",
        ),
        (
            MenuOption.ACTIVITY_RANGE,
            "get_activity_range",
            WeekSelection.CURRENT,
            "present_activity_list",
        ),
        (
            MenuOption.ACTIVITY_RANGE_PREV_WEEK,
            "get_activity_range",
            WeekSelection.PREVIOUS,
            "present_activity_list",
        ),
    ],
)
@pytest.mark.asyncio
async def test_activity_commands_select_week_and_typed_presenter(
    command_composition: CommandComposition,
    option: MenuOption,
    method_name: str,
    week: WeekSelection,
    presenter_name: str,
) -> None:
    method = getattr(command_composition.activities, method_name)

    result = await command_composition.registry.resolve(str(option.id)).execute()

    method.assert_awaited_once_with(week=week)
    command_composition.result_presenter.present_heading.assert_called_once_with(
        option.description
    )
    getattr(
        command_composition.result_presenter, presenter_name
    ).assert_called_once_with(result)


@pytest.mark.parametrize(
    ("option", "week"),
    [
        (MenuOption.STREAMS_CURRENT_WEEK, WeekSelection.CURRENT),
        (MenuOption.STREAMS_PREV_WEEK, WeekSelection.PREVIOUS),
    ],
)
@pytest.mark.asyncio
async def test_stream_export_commands_select_week_and_typed_presenter(
    command_composition: CommandComposition,
    option: MenuOption,
    week: WeekSelection,
) -> None:
    result = await command_composition.registry.resolve(str(option.id)).execute()

    command_composition.stream_export.export_streams_for_selected_week.assert_awaited_once_with(
        week=week
    )
    command_composition.result_presenter.present_heading.assert_called_once_with(
        option.description
    )
    command_composition.result_presenter.present_stream_export.assert_called_once_with(
        result
    )


@pytest.mark.parametrize(
    ("option", "method_name", "argument", "presenter_name"),
    [
        (
            MenuOption.SINGLE_STREAM,
            "get_streams_for_activity",
            123,
            "present_activity_stream",
        ),
        (
            MenuOption.MULTIPLE_STREAMS,
            "get_streams_for_multiple_activities",
            [123, 456],
            "present_stream_batch",
        ),
    ],
)
@pytest.mark.asyncio
async def test_stream_commands_use_prompted_ids_and_typed_presenter(
    command_composition: CommandComposition,
    option: MenuOption,
    method_name: str,
    argument: object,
    presenter_name: str,
) -> None:
    method = getattr(command_composition.streams, method_name)

    result = await command_composition.registry.resolve(str(option.id)).execute()

    method.assert_awaited_once_with(argument)
    getattr(
        command_composition.result_presenter, presenter_name
    ).assert_called_once_with(result)


@pytest.mark.asyncio
async def test_activity_zones_command_uses_prompted_id_and_typed_presenter(
    command_composition: CommandComposition,
) -> None:
    option = MenuOption.ACTIVITY_ZONES

    result = await command_composition.registry.resolve(str(option.id)).execute()

    command_composition.activity_zones.get_activity_zones.assert_awaited_once_with(123)
    command_composition.result_presenter.present_activity_zones.assert_called_once_with(
        result
    )


@pytest.mark.asyncio
async def test_weekly_summary_command_uses_its_required_typed_presenter(
    command_composition: CommandComposition,
) -> None:
    result = await command_composition.registry.resolve(
        str(MenuOption.WEEKLY_REPORT.id)
    ).execute()

    command_composition.summary.generate_summary.assert_awaited_once_with(
        week=WeekSelection.CURRENT
    )
    command_composition.summary_presenter.present_weekly_report.assert_called_once_with(
        result
    )
    command_composition.result_presenter.present_heading.assert_not_called()
