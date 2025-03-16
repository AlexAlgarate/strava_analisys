from typing import Dict

from src.access_token import GetAccessToken
from src.strava_api import StravaAPI
from src.utils import constants as constant
from src.utils import helpers as helper
from src.utils import printer_options as printer


def print_options(options: Dict[str, str]) -> None:
    print("\nChoose an option:")

    for key, value in options.items():
        print(f"{key}. {value}")


def main():
    logger = helper.Logger().setup_logger()
    access_token = GetAccessToken(logger=logger).get_access_token()
    strava_API = StravaAPI(access_token=access_token)
    while True:
        print_options(constant.PRINT_OPTIONS)
        choice = input("\nChoose an option (number or 'exit'): ")

        function_map = printer.get_function_map(
            api=strava_API, access_token=access_token
        )
        if choice.lower() == constant.EXIT_OPTION:
            print("\nGoodbye!\n")
            break

        if choice not in constant.PRINT_OPTIONS:
            print("\nNot a valid option. Please, enter a number or 'exit'.")
            continue

        print(f"\nOption choosen --> {choice}. {constant.PRINT_OPTIONS[choice]}\n")
        action = function_map.get(choice)
        if action:
            try:
                action()

            except Exception as e:
                logger.error(f"Error executing option: {e}", exc_info=True)
        else:
            print("\nNot a valid option.")


if __name__ == "__main__":
    main()
