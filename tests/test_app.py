import pathlib
import runpy
from unittest.mock import MagicMock, call, patch

from streamlit.testing.v1 import AppTest

import app

APP_PATH = pathlib.Path(__file__).parent.parent / "app.py"


def test_app_renders_without_exception():
    at = AppTest.from_file(APP_PATH).run()
    assert not at.exception


def test_app_renders_source_code_header():
    at = AppTest.from_file(APP_PATH).run()
    assert at.subheader[0].value == "Source Code"


def test_invalid_code_aborts_refactoring():
    with patch("analyzer.analyze_and_process_code") as mock_analyze:
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

        at = AppTest.from_file(APP_PATH).run()
        at.text_area[0].input("def broken_function(").run()
        at.button[0].click().run()

        results = at.session_state["analysis_results"]
        assert results is not None
        assert results["analysis"]["is_valid_code"] is False
        assert "Refactoring aborted" in results["refactored_code"]


def test_analysis_exception_displays_error():
    with patch("analyzer.analyze_and_process_code") as mock_analyze:
        mock_analyze.side_effect = RuntimeError("Groq API Timeout or Connection Error")

        at = AppTest.from_file(APP_PATH).run()
        at.text_area[0].input("print('Hello World')").run()
        at.button[0].click().run()

        assert len(at.error) > 0
        assert "Groq API Timeout or Connection Error" in at.error[0].value


def test_empty_input_guardrail():
    at = AppTest.from_file(APP_PATH).run()
    at.text_area[0].input("    ").run()
    at.button[0].click().run()

    assert len(at.warning) == 1
    assert at.warning[0].value == (
        "Please provide valid code input before running diagnostics."
    )


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

        at = AppTest.from_file(APP_PATH).run()
        at.text_area[0].input("print('100% coverage')").run()
        at.button[0].click().run()
        assert not at.exception

        markdown_values = [element.value for element in at.markdown]
        assert any("Missing docstring." in value for value in markdown_values)
        assert any("Add type hints." in value for value in markdown_values)


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

        at = AppTest.from_file(APP_PATH).run()
        at.text_area[0].input("pass").run()
        at.button[0].click().run()
        assert not at.exception

        success_messages = [element.value for element in at.success]
        assert "No major flaws detected." in success_messages
        assert "No suggestions generated." in success_messages


def test_render_suggestions_handles_multiple_items():
    with patch("app.st.expander"), patch("app.st.write") as mock_write:
        app._render_suggestions_section(
            {"suggestions": ["Suggestion A", "Suggestion B"]}
        )

    assert mock_write.call_args_list == [
        call("- Suggestion A"),
        call("- Suggestion B"),
    ]


def test_app_entrypoint_runs_main():
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
