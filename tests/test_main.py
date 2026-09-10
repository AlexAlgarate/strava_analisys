from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

import main as cli


@dataclass(frozen=True, slots=True)
class PatchedApplication:
    token_service: Mock
    api_context: MagicMock
    services: Mock
    menu: Mock
    api_factory: Mock
    token_service_factory: Mock
    services_factory: Mock
    menu_factory: Mock


def _patch_application(
    monkeypatch: pytest.MonkeyPatch,
    *,
    answers: tuple[object, ...],
) -> PatchedApplication:
    token_service = Mock()
    token_service.get_access_token.return_value = "access-token"
    api = Mock()
    api_context = MagicMock()
    api_context.__aenter__ = AsyncMock(return_value=api)
    api_context.__aexit__ = AsyncMock(return_value=None)
    services = Mock()
    services.activities = Mock()
    services.streams = Mock()
    services.stream_export = Mock()
    services.activity_zones = Mock()
    services.summary = Mock()
    menu = Mock()
    menu.execute_option = AsyncMock()
    menu.ask_option.side_effect = answers
    api_factory = Mock(return_value=api_context)
    token_service_factory = Mock(return_value=token_service)
    services_factory = Mock(return_value=services)
    menu_factory = Mock(return_value=menu)

    monkeypatch.setattr(cli, "setup_logging", Mock())
    monkeypatch.setattr(cli, "build_access_token_service", token_service_factory)
    monkeypatch.setattr(cli, "build_application_services", services_factory)
    monkeypatch.setattr(cli, "AsyncStravaAPI", api_factory)
    monkeypatch.setattr(cli, "MenuHandler", menu_factory)
    monkeypatch.setattr(cli, "create_console", Mock(return_value=Mock()))
    monkeypatch.setattr(cli, "ConsolePrompts", Mock(return_value=Mock()))
    return PatchedApplication(
        token_service=token_service,
        api_context=api_context,
        services=services,
        menu=menu,
        api_factory=api_factory,
        token_service_factory=token_service_factory,
        services_factory=services_factory,
        menu_factory=menu_factory,
    )


@pytest.mark.asyncio
async def test_run_cli_wires_and_runs_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patched = _patch_application(monkeypatch, answers=("1", "q"))

    await cli.run_cli()

    patched.token_service_factory.assert_called_once_with()
    patched.token_service.get_access_token.assert_called_once_with()
    patched.api_factory.assert_called_once_with(access_token="access-token")
    patched.services_factory.assert_called_once_with(
        patched.api_context.__aenter__.return_value
    )
    dependencies = patched.menu_factory.call_args.args[0]
    assert isinstance(dependencies, cli.MenuDependencies)
    assert dependencies.activities is patched.services.activities
    assert dependencies.streams is patched.services.streams
    assert dependencies.stream_export is patched.services.stream_export
    assert dependencies.activity_zones is patched.services.activity_zones
    assert dependencies.summary is patched.services.summary
    patched.menu.print_welcome.assert_called_once_with()
    assert patched.menu.print_menu.call_count == 2
    patched.menu.execute_option.assert_awaited_once_with("1")
    patched.menu.print_goodbye.assert_called_once_with()
    patched.api_context.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("interruption", [EOFError(), KeyboardInterrupt()])
async def test_run_cli_exits_gracefully_on_terminal_interrupt(
    monkeypatch: pytest.MonkeyPatch,
    interruption: BaseException,
) -> None:
    patched = _patch_application(monkeypatch, answers=(interruption,))

    await cli.run_cli()

    patched.menu.print_goodbye.assert_called_once_with()


def test_main_runs_async_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    run_cli = AsyncMock()
    asyncio_run = Mock()
    monkeypatch.setattr(cli, "run_cli", run_cli)
    monkeypatch.setattr(cli.asyncio, "run", asyncio_run)

    cli.main()

    asyncio_run.assert_called_once()
    run_cli.assert_called_once_with()
    asyncio_run.call_args.args[0].close()
