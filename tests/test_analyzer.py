from unittest.mock import patch

import pytest
import streamlit as st

from analyzer import analyze_and_process_code, create_client, validate_analysis_response


def test_validate_analysis_response_success():
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

    assert validate_analysis_response(None) is False
    assert validate_analysis_response("not a dictionary") is False


def test_validate_analysis_response_invalid_types():
    """Verify validation fails when data types are inccorect."""
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

    # Test invalid type for is_valid_code (Triggers Line 75)
    bad_bool_payload = base_payload.copy()
    bad_bool_payload["is_valid_code"] = "not a boolean string"
    assert validate_analysis_response(bad_bool_payload) is False

    # Systematically corrupt every individual text field
    for key in ["language", "extension", "refactored_code", "readme_content"]:
        bad_payload = base_payload.copy()
        bad_payload[key] = 123
        assert validate_analysis_response(bad_payload) is False

    # Test invalid type for big_o
    bad_big_o = base_payload.copy()
    bad_big_o["big_o"] = "Not a dict"
    assert validate_analysis_response(bad_big_o) is False

    # Test invalid type for flaws/suggestions
    bad_flaws = base_payload.copy()
    bad_flaws["flaws"] = "Not a list"
    assert validate_analysis_response(bad_flaws) is False


def test_create_client_secrets_exception_handling():
    """Ensure that secret handling works as expected."""
    with patch("analyzer.load_dotenv"), patch(
        "analyzer.os.getenv"
    ) as mock_getenv, patch("analyzer.Groq"), patch.object(
        st, "secrets", side_effect=TypeError("Simulated error")
    ):

        mock_getenv.return_value = "fallback_env_key"

        client = create_client()
        assert client is not None


def test_create_client_with_secrets():
    """Verify create_client successfully extracts the key from st.secrets."""
    with patch("analyzer.st.secrets", {"GROQ_API_KEY": "secret_key"}), patch(
        "analyzer.Groq"
    ) as mock_groq:
        client = create_client()
        mock_groq.assert_called_once_with(api_key="secret_key")
        assert client is not None


def test_create_client_missing_key_error():
    """Verify create_client raises ValueError when no keys are found anywhere."""
    with patch("analyzer.st.secrets", {}), patch("analyzer.load_dotenv"), patch(
        "analyzer.os.getenv", return_value=None
    ):
        with pytest.raises(ValueError, match="GROQ_API_KEY could not be found"):
            create_client()


@patch("analyzer.Groq")
def test_analyze_code_invalid_structure(mock_groq_class):
    """Verify analyizing faulty responses triggers backup response."""
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
    assert res["is_valid_code"] is False
