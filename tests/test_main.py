from unittest.mock import Mock

import pytest

import main as cli


def test_main_wires_the_application_without_real_credentials(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    setup_logging = Mock()
    token_provider = Mock()
    token_provider.get_access_token.return_value = "access-token"
    token_provider_factory = Mock(return_value=token_provider)
    api = Mock()
    api_factory = Mock(return_value=api)
    service = Mock()
    service_factory = Mock(return_value=service)
    summary_service = Mock()
    summary_service_factory = Mock(return_value=summary_service)
    menu = Mock()
    menu_factory = Mock(return_value=menu)
    answers = iter(("1", "q"))

    monkeypatch.setattr(cli, "setup_logging", setup_logging)
    monkeypatch.setattr(cli, "GetAccessToken", token_provider_factory)
    monkeypatch.setattr(cli, "AsyncStravaAPI", api_factory)
    monkeypatch.setattr(cli, "StravaService", service_factory)
    monkeypatch.setattr(cli, "ActivitySummaryService", summary_service_factory)
    monkeypatch.setattr(cli, "MenuHandler", menu_factory)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    cli.main()

    setup_logging.assert_called_once_with()
    token_provider.get_access_token.assert_called_once_with()
    api_factory.assert_called_once_with(access_token="access-token")
    summary_service_factory.assert_called_once_with(activity_provider=service)
    assert menu_factory.call_args.kwargs["service"] is service
    assert menu_factory.call_args.kwargs["summary_service"] is summary_service
    assert menu.print_menu.call_count == 2
    menu.execute_option.assert_called_once_with("1")
    assert "Goodbye" in capsys.readouterr().out
