from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st
from dotenv import load_dotenv
from streamlit_navigation_bar import st_navbar

from analyzer import analyze_and_process_code
from utils import MAX_CODE_LENGTH, get_navbar_options, get_navbar_styles


def _get_language_and_extension(analysis: Optional[Dict[str, Any]]) -> tuple[str, str]:
    if not analysis:
        return "python", ".py"
    return analysis.get("language", "python"), analysis.get("extension", ".py")


def _build_error_results(combined_results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "analysis": combined_results,
        "refactored_code": "Error: Input does not appear to be valid source code. Refactoring aborted.",  # noqa: E501
        "readme_content": "Error: Cannot generate documentation for invalid source code.",  # noqa: E501
    }


def _build_success_results(combined_results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "analysis": combined_results,
        "refactored_code": combined_results.get("refactored_code", ""),
        "readme_content": combined_results.get("readme_content", ""),
    }


def _build_pipeline_failure_results(combined_results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "analysis": combined_results,
        "refactored_code": "Error: Process pipeline failure. Refactoring aborted.",  # noqa: E501
        "readme_content": "Error: Process pipeline failure. Please try again.",  # noqa: E501
    }


def analyze(user_input: str) -> None:
    if not user_input.strip():
        st.warning("Please provide valid code input before running diagnostics.")
        return

    try:
        with st.spinner("Analyzing, refactoring, and documenting code..."):
            combined_results = analyze_and_process_code(user_input)
            is_valid = combined_results.get("is_valid_code")
            if is_valid is True:
                st.session_state.analysis_results = _build_success_results(
                    combined_results
                )
            elif is_valid is False:
                st.session_state.analysis_results = _build_error_results(
                    combined_results
                )
            else:
                st.session_state.analysis_results = _build_pipeline_failure_results(
                    combined_results
                )

    except Exception as error:
        st.error(f"Analysis failed:\n{error}")


def _set_page_config() -> None:
    st.set_page_config(
        page_title="Code Buddy",
        page_icon="Images/smile_icon.png",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def _hide_streamlit_buttons() -> None:
    st.markdown(
        """
    <style>
    .stAppDeployButton {
        display: none;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="st-navbar"] > div {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    [data-testid="st-navbar"] > div > div {
        flex: 0 1 auto !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def _initialize_session_state() -> None:
    """Safely keep results across hot-reloads."""
    if (
        "analysis_results" not in st.session_state
    ):  # This preseves any data on the site if the user clicks a button
        st.session_state.analysis_results = None


def _render_complexity_section(analysis: Optional[Dict[str, Any]]) -> None:
    with st.expander("**Complexity**", expanded=True):
        if analysis is None:
            st.write("Please run the code analysis to find the complexity.")
        else:
            big_o = analysis.get("big_o", {})
            st.write(
                f"Time Complexity: {big_o.get('time', 'Unknown')}  \n",
                f"Space Complexity: {big_o.get('space', 'Unknown')}  \n\n",
                big_o.get("explanation", "No explanation provided."),
            )


def _render_bulleted_list_or_success(items: list[str], empty_message: str) -> None:
    if items:
        for item in items:
            st.write(f"- {item}")
    else:
        st.success(empty_message)


def _render_flaws_section(analysis: Optional[Dict[str, Any]]) -> None:
    with st.expander("**Identified Flaws**", expanded=False):
        if analysis is None:
            st.write("Please run the code analysis to find flaws.")
        else:
            _render_bulleted_list_or_success(
                analysis.get("flaws", []), "No major flaws detected."
            )


def _render_suggestions_section(analysis: Optional[Dict[str, Any]]) -> None:
    with st.expander("**Suggestions**", expanded=False):
        if analysis is None:
            st.write("Please run the code analysis to find suggestions.")
        else:
            _render_bulleted_list_or_success(
                analysis.get("suggestions", []), "No suggestions generated."
            )


def _render_refactored_code_section(
    refactored_code: Optional[str], language: str = "python"
) -> None:
    """Render syntax highlighted refactored code.

    Args:
        refactored_code (Optional[str]): Processed optimization logic string.
        language (str): Target text syntax type parsing target used by code blocks.
    """
    with st.expander("**Refactored Code**", expanded=False):
        if refactored_code is None:
            st.write("Please run the code analysis to get refactored code.")
        else:
            st.code(refactored_code, language=language)


def _render_readme_section(readme_content: Optional[str]) -> None:
    with st.expander("**Generated README**", expanded=False):
        if readme_content is None:
            st.write("Please run the code analysis to get the generated README.")
        else:
            st.markdown(readme_content)


def _render_download_buttons(
    refactored_code: Optional[str],
    readme_content: Optional[str],
    extension: str = ".py",
) -> None:
    if (readme_content is not None) and (refactored_code is not None):
        st.markdown("---")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="💾 Download Code",
                data=refactored_code,
                file_name=f"refactored_code{extension}",
                mime="text/plain",
                use_container_width=True,
            )
        with d_col2:
            st.download_button(
                label="📖 Download README",
                data=readme_content,
                file_name="README.md",
                mime="text/markdown",
                use_container_width=True,
            )


def render_analysis_ui(
    analysis: Optional[Dict[str, Any]] = None,
    refactored_code: Optional[str] = None,
    readme_content: Optional[str] = None,
) -> None:
    language, extension = _get_language_and_extension(analysis)
    _render_complexity_section(analysis)
    _render_flaws_section(analysis)
    _render_suggestions_section(analysis)
    _render_refactored_code_section(refactored_code, language=language)
    _render_readme_section(readme_content)
    _render_download_buttons(refactored_code, readme_content, extension=extension)


def _render_input_panel() -> str:
    st.subheader("Source Code")
    user_input = st.text_area(
        "Source Code",
        max_chars=MAX_CODE_LENGTH,
        height=600,
        placeholder="Paste code here...",
        label_visibility="collapsed",
    )

    if st.button(
        "Analyze & Refactor",
        type="primary",
        use_container_width=True,
    ):
        analyze(user_input)
    return user_input


def _render_results_panel() -> None:
    st.markdown(
        "<h3 style='text-align: center;'> Results</h3>",
        unsafe_allow_html=True,
    )
    results = st.session_state.analysis_results
    if results is not None:
        render_analysis_ui(
            analysis=results["analysis"],
            refactored_code=results["refactored_code"],
            readme_content=results["readme_content"],
        )
    else:
        render_analysis_ui(None, None, None)


def _render_main_layout() -> None:
    col1, col2 = st.columns(2)
    with col1:
        _render_input_panel()
    with col2:
        _render_results_panel()


def _render_navbar() -> None:
    st_navbar(
        ["About"],
        "Home",
        logo_path="Images/logo-cascadia.svg",
        logo_page="Home",
        urls={"About": "https://github.com/thealexandermulder/CODE_BUDDY"},
        styles=get_navbar_styles(),
        options=get_navbar_options(),  # pyright: ignore[reportArgumentType]
        adjust=False,
    )


def main() -> None:
    _set_page_config()
    _hide_streamlit_buttons()
    _render_navbar()
    load_dotenv()
    _initialize_session_state()
    _render_main_layout()


if __name__ == "__main__":
    main()
