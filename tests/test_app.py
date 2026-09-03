import os
import pathlib
import runpy
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest

import app

APP_PATH = pathlib.Path(__file__).parent.parent / "app.py"
os.environ["STREAMLIT_TESTING"] = "1"


def test_app_renders_properly():
    at = AppTest.from_file("APP_PATH").run()
    assert not at.exception
    assert at.subheader[0].value == "Source Code"


def test_invalid_syntax_error_handling():
    with patch("app.analyze") as mock_analyze:
        mock_analyze.return_value = {
            "is_valid_code": False,
            "language": "python",
            "extension": ".py",
            "big_o": {
                "time": "Unknown",
                "space": "Unknown",
                "explanation": "Broken syntax.",
            },
            "flaws": ["Invalid syntax."],
            "suggestions": [],
        }

        at = AppTest.from_file("APP_PATH").run()
        at.text_area[0].input("def broken_function(").run()
        at.button[0].click().run()

        results = at.session_state["analysis_results"]
        assert results is not None
        assert "Refactoring aborted" in results["refactored_code"]


def test_analyze_exception_handling():
    with patch("analyzer.analyze_and_process_code") as mock_analyze:
        mock_analyze.side_effect = RuntimeError("Groq API Timeout or Connection Error")

        at = AppTest.from_file("APP_PATH").run()
        at.text_area[0].input("print('Hello World')").run()
        at.button[0].click().run()

        assert len(at.error) > 0


def test_empty_input_guardrail():
    at = AppTest.from_file("APP_PATH").run()
    at.text_area[0].input("    ").run()
    at.button[0].click().run()

    assert len(at.warning) > 0


def test_ui_renders_flaws_and_suggestions():
    with patch("analyzer.analyze_and_process_code") as mock_analyze:
        mock_analyze.return_value = {
            "is_valid_code": True,
            "language": "python",
            "extension": ".py",
            "big_o": {"time": "O(n)", "space": "O(1)", "explanation": "Looping."},
            "flaws": ["Missing docstring."],
            "suggestions": ["Add type hints."],
            "refactored_code": "def func(): pass",
            "readme_content": "# Done",
        }

        at = AppTest.from_file("APP_PATH").run()
        at.text_area[0].input("print('100% coverage')").run()
        at.button[0].click().run()
        assert not at.exception


def test_ui_renders_empty_flaws_and_suggestions():
    with patch("analyzer.analyze_and_process_code") as mock_analyze:
        mock_analyze.return_value = {
            "is_valid_code": True,
            "language": "python",
            "extension": ".py",
            "big_o": {"time": "O(1)", "space": "O(1)", "explanation": "Constant time."},
            "flaws": [],
            "suggestions": [],
            "refactored_code": "pass",
            "readme_content": "# Done Empty",
        }

        at = AppTest.from_file("APP_PATH").run()
        at.text_area[0].input("pass").run()
        at.button[0].click().run()
        assert not at.exception


def test_direct_render_suggestions_loop_coverage():
    with patch("app.st.expander"):
        app._render_suggestions_section(
            {"suggestions": ["Suggestion A", "Suggestion B"]}
        )


def test_main_block_execution():
    with patch("app._set_page_config"), patch("app._hide_streamlit_buttons"), patch(
        "app.st_navbar"
    ), patch("app.load_dotenv"), patch("app._initialize_session_state"), patch(
        "app.st.columns", return_value=(MagicMock(), MagicMock())
    ), patch(
        "app.st.markdown"
    ), patch(
        "app.render_analysis_ui"
    ):

        runpy.run_module("app", run_name="__main__")
