from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

import main as cli


def _patch_application(
    monkeypatch: pytest.MonkeyPatch,
    *,
    answers: tuple[object, ...],
) -> tuple[Mock, MagicMock, Mock, Mock, Mock, Mock, Mock, Mock]:
    token_provider = Mock()
    token_provider.get_access_token.return_value = "access-token"
    api = Mock()
    api_context = MagicMock()
    api_context.__aenter__ = AsyncMock(return_value=api)
    api_context.__aexit__ = AsyncMock(return_value=None)
    service = Mock()
    summary_service = Mock()
    menu = Mock()
    menu.execute_option = AsyncMock()
    menu.ask_option.side_effect = answers
    api_factory = Mock(return_value=api_context)
    summary_service_factory = Mock(return_value=summary_service)
    menu_factory = Mock(return_value=menu)

    monkeypatch.setattr(cli, "setup_logging", Mock())
    monkeypatch.setattr(cli, "GetAccessToken", Mock(return_value=token_provider))
    monkeypatch.setattr(cli, "AsyncStravaAPI", api_factory)
    monkeypatch.setattr(cli, "StravaService", Mock(return_value=service))
    monkeypatch.setattr(
        cli,
        "ActivitySummaryService",
        summary_service_factory,
    )
    monkeypatch.setattr(cli, "MenuHandler", menu_factory)
    monkeypatch.setattr(cli, "create_console", Mock(return_value=Mock()))
    monkeypatch.setattr(cli, "ConsolePrompts", Mock(return_value=Mock()))
    return (
        token_provider,
        api_context,
        service,
        summary_service,
        menu,
        api_factory,
        summary_service_factory,
        menu_factory,
    )


@pytest.mark.asyncio
async def test_run_cli_wires_and_runs_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        token_provider,
        api_context,
        service,
        summary_service,
        menu,
        api_factory,
        summary_service_factory,
        menu_factory,
    ) = _patch_application(monkeypatch, answers=("1", "q"))

    await cli.run_cli()

    token_provider.get_access_token.assert_called_once_with()
    api_factory.assert_called_once_with(access_token="access-token")
    summary_service_factory.assert_called_once_with(activity_provider=service)
    dependencies = menu_factory.call_args.args[0]
    assert isinstance(dependencies, cli.MenuDependencies)
    assert dependencies.service is service
    assert dependencies.summary_service is summary_service
    menu.print_welcome.assert_called_once_with()
    assert menu.print_menu.call_count == 2
    menu.execute_option.assert_awaited_once_with("1")
    menu.print_goodbye.assert_called_once_with()
    api_context.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("interruption", [EOFError(), KeyboardInterrupt()])
async def test_run_cli_exits_gracefully_on_terminal_interrupt(
    monkeypatch: pytest.MonkeyPatch,
    interruption: BaseException,
) -> None:
    patched_application = _patch_application(monkeypatch, answers=(interruption,))
    menu = patched_application[4]

    await cli.run_cli()

    menu.print_goodbye.assert_called_once_with()


def test_main_runs_async_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    run_cli = AsyncMock()
    asyncio_run = Mock()
    monkeypatch.setattr(cli, "run_cli", run_cli)
    monkeypatch.setattr(cli.asyncio, "run", asyncio_run)

    cli.main()

    asyncio_run.assert_called_once()
    run_cli.assert_called_once_with()
    asyncio_run.call_args.args[0].close()
