from contextlib import nullcontext
from io import StringIO
from unittest.mock import Mock

from rich.console import Console

from src.presentation.console_output.progress import ConsoleProgress


def test_tracks_operation_with_console_status() -> None:
    console = Mock(spec=Console)
    console.status.return_value = nullcontext()

    with ConsoleProgress(console).track("Loading activities"):
        pass

    console.status.assert_called_once_with(
        "[accent]Loading activities…[/accent]",
        spinner="dots",
    )


def test_real_status_renders_without_errors() -> None:
    output = StringIO()
    console = Console(file=output, force_terminal=False)

    with ConsoleProgress(console).track("Loading"):
        pass

    assert output.getvalue() == ""
