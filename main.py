import getpass
from typing import Dict

from src.access_token import GetAccessToken
from src.strava_api import StravaAPI
from src.utils import constant, helper, printer


def print_options(options: Dict[str, str]) -> None:
    print("\nChoose an option:")

    for key, value in options.items():
        print(f"{key}. {value}")


def main():
    access_token = GetAccessToken().get_access_token()
    Strava_API = StravaAPI(access_token=access_token)
    logger = helper.Logger().setup_logger()
    while True:
        print_options(constant.print_options_main)
        choice = getpass.getpass(
            f"Choose an option: (1 to {len(constant.print_options_main)}) "
        )

        function_map = printer.get_function_map(
            api=Strava_API, access_token=access_token
        )

        if choice == "8":
            print("\nGoodbye!")
            break
        print(f"\nOption choosen --> {choice}. {constant.print_options_main[choice]}")
        action = function_map.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                logger.error(f"Error executing option: {e}")
        else:
            print("\nNot a valid option.")


if __name__ == "__main__":
    main()
