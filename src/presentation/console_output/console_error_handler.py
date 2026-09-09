class ConsoleErrorHandler:
    def print_error(self, option: str) -> None:
        self._print_error_header(option)
        self._print_usage_hint()

    def _print_error_header(self, option: str) -> None:
        print("\n❌ Invalid option selected:")
        print(f"   '{option}' is not a valid menu choice\n")

    def _print_usage_hint(self) -> None:
        print("Please select a number from the menu or 'q' to quit\n")
