from collections.abc import Iterator
from io import StringIO

from rich.console import Console

from src.presentation.console_output.console import STRAVA_THEME
from src.presentation.console_output.prompts import ConsolePrompts


def _prompts(*answers: str) -> tuple[ConsolePrompts, StringIO]:
    responses: Iterator[str] = iter(answers)
    output = StringIO()
    console = Console(
        file=output,
        theme=STRAVA_THEME,
        color_system=None,
        width=100,
    )
    return ConsolePrompts(console, lambda _prompt: next(responses)), output


def test_menu_prompt_normalizes_input_without_owning_catalog_validation() -> None:
    prompts, output = _prompts(" UNKNOWN ")

    result = prompts.ask_menu_option()

    assert result == "unknown"
    assert output.getvalue() == ""


def test_menu_prompt_accepts_case_insensitive_quit() -> None:
    prompts, _ = _prompts(" Q ")

    assert prompts.ask_menu_option() == "q"


def test_activity_id_prompt_retries_invalid_values() -> None:
    prompts, output = _prompts("", "runner", "-2", " 42 ")

    result = prompts.ask_activity_id()

    assert result == 42
    assert "cannot be empty" in output.getvalue()
    assert "whole number" in output.getvalue()
    assert "must be positive" in output.getvalue()


def test_activity_ids_prompt_deduplicates_while_preserving_order() -> None:
    prompts, _ = _prompts("1, 2,1, 3")

    assert prompts.ask_activity_ids() == [1, 2, 3]


def test_activity_ids_prompt_retries_when_one_id_is_invalid() -> None:
    prompts, output = _prompts("1,nope", "4,5")

    assert prompts.ask_activity_ids() == [4, 5]
    assert "whole number" in output.getvalue()
