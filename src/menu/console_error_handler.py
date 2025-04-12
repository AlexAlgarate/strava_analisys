from src.interfaces.console_printer import PrinterErrorInterface
from src.menu.options import MenuOption


class ConsoleErrorHandler(PrinterErrorInterface):
    def print_error(self, option: str) -> None:
        valid_options = {str(opt.id): opt for opt in MenuOption}
        print(f"\n❌ Invalid option: {option}\n")
        print(f"Valid options are: {', '.join(valid_options.keys())}\n")
