from src.presentation.menu.options import MenuCategory, MenuOption


def test_menu_options_have_stable_unique_ids() -> None:
    ids = [option.id for option in MenuOption]

    assert ids == list(range(1, 11))
    assert len(ids) == len(set(ids))


def test_menu_options_have_descriptions_and_categories() -> None:
    for option in MenuOption:
        assert option.description
        assert isinstance(option.category, MenuCategory)


def test_options_cover_each_menu_category() -> None:
    categories = {option.category for option in MenuOption}

    assert categories == set(MenuCategory)


def test_menu_option_string_representation() -> None:
    assert str(MenuOption.ACTIVITY_DETAILS) == "MenuOption.ACTIVITY_DETAILS"
