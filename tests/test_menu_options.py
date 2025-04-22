import pytest

import src.menu.options as options_module

# from src.menu.options import MenuOption
# from src.utils.constants import MENU_DESCRIPTIONS


class TestMenuOption:
    def test_menu_option_values(self):
        assert options_module.MenuOption.ONE_ACTIVITY.id == 1
        assert options_module.MenuOption.LAST_200_ACTIVITIES.id == 2
        assert options_module.MenuOption.ACTIVITY_DETAILS.id == 3

    def test_menu_option_descriptions(self):
        for option in options_module.MenuOption:
            assert (
                option.description
                == options_module.constants.MENU_DESCRIPTIONS[option.name]
            )

    def test_validate_descriptions_success(self):
        # Should not raise any exception
        options_module.MenuOption.validate_descriptions()

    def test_validate_descriptions_missing(self, monkeypatch):
        from src import utils

        incomplete = utils.constants.MENU_DESCRIPTIONS.copy()
        del incomplete["ONE_ACTIVITY"]

        monkeypatch.setitem(utils.constants.__dict__, "MENU_DESCRIPTIONS", incomplete)

        from src.menu.options import MenuOption

        with pytest.raises(
            ValueError, match="Missing descriptions for menu options: ONE_ACTIVITY"
        ):
            MenuOption.validate_descriptions()

    def test_menu_option_str_representation(self):
        assert str(options_module.MenuOption.ONE_ACTIVITY) == "MenuOption.ONE_ACTIVITY"

    def test_menu_option_equality(self):
        assert (
            options_module.MenuOption.ONE_ACTIVITY
            == options_module.MenuOption.ONE_ACTIVITY
        )
        assert (
            options_module.MenuOption.ONE_ACTIVITY
            != options_module.MenuOption.LAST_200_ACTIVITIES
        )
