import pytest

import src.presentation.menu.options as options_module


class TestMenuOption:
    def test_menu_option_values(self) -> None:
        assert options_module.MenuOption.ACTIVITY_DETAILS.id == 1
        assert options_module.MenuOption.ACTIVITY_DETAILS_PREV_WEEK.id == 2
        assert options_module.MenuOption.SINGLE_STREAM.id == 5

    def test_menu_option_descriptions(self) -> None:
        for option in options_module.MenuOption:
            assert option.description == options_module.MENU_DESCRIPTIONS[option.name]

    def test_validate_descriptions_success(self) -> None:
        # Should not raise any exception
        options_module.MenuOption.validate_descriptions()

    def test_validate_descriptions_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        incomplete = options_module.MENU_DESCRIPTIONS.copy()
        del incomplete["ACTIVITY_DETAILS"]

        monkeypatch.setitem(options_module.__dict__, "MENU_DESCRIPTIONS", incomplete)

        from src.presentation.menu.options import MenuOption

        with pytest.raises(
            ValueError,
            match="Missing descriptions for menu options: ACTIVITY_DETAILS",
        ):
            MenuOption.validate_descriptions()

    def test_menu_option_str_representation(self) -> None:
        assert (
            str(options_module.MenuOption.ACTIVITY_DETAILS)
            == "MenuOption.ACTIVITY_DETAILS"
        )

    def test_menu_option_equality(self) -> None:
        assert (
            options_module.MenuOption.ACTIVITY_DETAILS
            == options_module.MenuOption.ACTIVITY_DETAILS
        )
        assert (
            options_module.MenuOption.ACTIVITY_DETAILS
            != options_module.MenuOption.ACTIVITY_DETAILS_PREV_WEEK
        )
