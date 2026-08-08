from typing import Dict

MAX_CODE_LENGTH = 15000


def get_navbar_styles() -> Dict[str, Dict[str, str]]:
    return {
        "nav": {
            "background-color": "var(--primary-color)",
            "align-items": "center",
            "font-family": "Cascadia Code",
            "padding-top": "1rem",
            "padding-bottom": "1rem",
            "display": "flex",
        },
        "div": {"max-width": "100%"},
        "span": {
            "justify-content": "right",
            "color": "var(--text-color)",
            "font-weight": "normal",
            "font-size": "14px",
        },
        "img": {"height": "50px", "width": "auto"},
        "active": {"color": "var(--text-color)"},
        "hover": {"color": "var(--text-color)"},
    }


def get_navbar_options() -> Dict[str, bool]:
    return {"show_menu": False, "show_sidebar": False, "hide_nav": True}
