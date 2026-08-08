from utils import get_navbar_styles


def test_navbar_styles_structure():
    styles = get_navbar_styles()
    assert isinstance(styles, dict)
    assert "nav" in styles
    assert styles["nav"]["font-family"] == "Cascadia Code"
