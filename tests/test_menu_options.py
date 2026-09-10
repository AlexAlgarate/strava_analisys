from src.presentation.menu.options import MenuCategory, MenuOption


def test_menu_options_have_stable_unique_ids() -> None:
    expected_ids = {
        MenuOption.ACTIVITY_DETAILS: 1,
        MenuOption.ACTIVITY_DETAILS_PREV_WEEK: 2,
        MenuOption.ACTIVITY_LIST: 3,
        MenuOption.ACTIVITY_LIST_PREV_WEEK: 4,
        MenuOption.SINGLE_STREAM: 5,
        MenuOption.MULTIPLE_STREAMS: 6,
        MenuOption.STREAMS_CURRENT_WEEK: 7,
        MenuOption.STREAMS_PREV_WEEK: 8,
        MenuOption.WEEKLY_REPORT: 9,
        MenuOption.ACTIVITY_ZONES: 10,
        MenuOption.EXPORT_ACTIVITY_ZONES: 11,
    }
    actual_ids = {option: option.id for option in MenuOption}

    assert actual_ids == expected_ids
    assert all(option_id > 0 for option_id in actual_ids.values())
    assert len(actual_ids.values()) == len(set(actual_ids.values()))


def test_menu_options_have_descriptions_and_categories() -> None:
    for option in MenuOption:
        assert option.description
        assert isinstance(option.category, MenuCategory)


def test_options_cover_each_menu_category() -> None:
    categories = {option.category for option in MenuOption}

    assert categories == set(MenuCategory)


def test_menu_option_string_representation() -> None:
    assert str(MenuOption.ACTIVITY_DETAILS) == "MenuOption.ACTIVITY_DETAILS"
