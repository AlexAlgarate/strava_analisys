from src.presentation.console_output.console import create_console


def test_create_console_registers_application_theme() -> None:
    console = create_console()

    assert console.get_style("accent").color is not None
    assert console.get_style("success").bold is True
