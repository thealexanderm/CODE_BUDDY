import json
from unittest.mock import MagicMock, patch

import pytest
import streamlit as st

from analyzer import analyze_and_process_code, create_client, validate_analysis_response


def test_validate_analysis_response_accepts_valid_data():
    valid_data = {
        "is_valid_code": True,
        "language": "python",
        "extension": ".py",
        "big_o": {
            "time": "O(n)",
            "space": "O(1)",
            "explanation": "Simple loop.",
        },
        "flaws": ["None"],
        "suggestions": ["Add type hints"],
        "refactored_code": "def typed_function() -> None:\n    pass",
        "readme_content": "# Readme Markdown",
    }
    assert validate_analysis_response(valid_data) is True


def test_validate_analysis_response_missing_key():
    invalid_data = {"big_o": {"time": "O(n)", "space": "O(1)", "explanation": "..."}}
    assert validate_analysis_response(invalid_data) is False


@pytest.mark.parametrize("invalid_data", [None, "not a dictionary"])
def test_validate_analysis_response_rejects_non_dict_values(invalid_data):
    assert validate_analysis_response(invalid_data) is False


def test_validate_analysis_response_invalid_types():
    base_payload = {
        "is_valid_code": True,
        "language": "python",
        "extension": ".py",
        "big_o": {"time": "O(1)", "space": "O(1)", "explanation": "clear"},
        "flaws": ["None"],
        "suggestions": ["None"],
        "refactored_code": "pass",
        "readme_content": "# Readme",
    }

    bad_bool_payload = base_payload.copy()
    bad_bool_payload["is_valid_code"] = "not a boolean string"
    assert validate_analysis_response(bad_bool_payload) is False

    for key in ["language", "extension", "refactored_code", "readme_content"]:
        bad_payload = base_payload.copy()
        bad_payload[key] = 123
        assert validate_analysis_response(bad_payload) is False

    bad_big_o = base_payload.copy()
    bad_big_o["big_o"] = "Not a dict"
    assert validate_analysis_response(bad_big_o) is False

    bad_flaws = base_payload.copy()
    bad_flaws["flaws"] = "Not a list"
    assert validate_analysis_response(bad_flaws) is False

    bad_suggestions = base_payload.copy()
    bad_suggestions["suggestions"] = "Not a list"
    assert validate_analysis_response(bad_suggestions) is False


def test_create_client_env_fallback():
    with patch("analyzer.load_dotenv"), patch(
        "analyzer.os.getenv"
    ) as mock_getenv, patch("analyzer.Groq") as mock_groq, patch.object(
        st, "secrets", side_effect=TypeError("Simulated error")
    ):

        mock_getenv.return_value = "fallback_env_key"

        client = create_client()
        assert client is not None
        mock_groq.assert_called_once_with(api_key="fallback_env_key")


def test_create_client_uses_streamlit_secrets():
    with patch("analyzer.load_dotenv"), patch(
        "analyzer.st.secrets", {"GROQ_API_KEY": "secret_key"}
    ), patch("analyzer.Groq") as mock_groq:
        client = create_client()
        mock_groq.assert_called_once_with(api_key="secret_key")
        assert client is not None


def test_create_client_missing_api_key_error():
    with patch("analyzer.st.secrets", {}), patch("analyzer.load_dotenv"), patch(
        "analyzer.os.getenv", return_value=None
    ):
        with pytest.raises(ValueError, match="GROQ_API_KEY could not be found"):
            create_client()


def test_analyze_code_returns_failure_for_malformed_json():
    with patch("analyzer.Groq") as mock_groq_class:
        mock_client = mock_groq_class.return_value
        mock_chat = mock_client.chat.completions.create
        mock_chat.return_value.choices = [
            type(
                "Choice",
                (object,),
                {
                    "message": type(
                        "Message", (object,), {"content": '{"malformed_json":'}
                    )()
                },
            )()
        ]

        res = analyze_and_process_code("some code")
        assert res["is_valid_code"] is None
        assert "Process pipeline failure" in res["refactored_code"]


def test_analyze_code_returns_valid_response():
    valid_response = {
        "is_valid_code": True,
        "language": "python",
        "extension": ".py",
        "big_o": {
            "time": "O(n)",
            "space": "O(1)",
            "explanation": "Simple loop.",
        },
        "flaws": [],
        "suggestions": [],
        "refactored_code": "pass",
        "readme_content": "# Readme",
    }

    fake_response = MagicMock()
    fake_response.choices[0].message.content = json.dumps(valid_response)

    with patch("analyzer.Groq") as mock_groq:
        mock_groq.return_value.chat.completions.create.return_value = fake_response

        result = analyze_and_process_code("some code")

    assert result == valid_response


def test_analyze_code_retries_when_response_content_is_none():
    fake_response = MagicMock()
    fake_response.choices[0].message.content = None

    with patch("analyzer.Groq") as mock_groq_class:
        mock_chat = mock_groq_class.return_value.chat.completions.create
        mock_chat.return_value = fake_response

        result = analyze_and_process_code("some code")

    assert result["is_valid_code"] is None
    assert mock_chat.call_count == 3
