"""Clipboard component for Streamlit.

This module exposes a single function, :func:`st_copy_to_clipboard`, which
renders a button in your Streamlit app.  When clicked, the button
attempts to write the provided text to the user's clipboard using
modern Web APIs.  On success or failure the component returns a
status string which can be used to present feedback to the user.

The implementation is backed by a small custom component written in
React that lives in the `frontend/` subdirectory.  When packaging
this project, be sure to run `npm install && npm run build` in that
directory so that the compiled assets exist in `frontend/build`.
"""

from pathlib import Path
from typing import Optional
import os

import streamlit as st
import streamlit.components.v1 as components

# Determine the absolute path to the build directory for the frontend.
_parent_dir = Path(__file__).absolute().parent
_build_dir = _parent_dir / "frontend" / "build"

# Read the component name from the package.json file.
_component_name = "copy_to_clipboard"

if _build_dir.exists():
    _component_func = components.declare_component(
        _component_name,
        path=str(_build_dir)
    )
else:
    # In development mode (frontend not yet built), fall back to
    # Streamlit's dev server which runs the component in dev mode.
    # If we're not in development mode, raise an exception.
    if os.environ.get("STREAMLIT_DEVELOPMENT_MODE") == "true":
        _component_func = components.declare_component(
            _component_name,
            url="http://localhost:3000"
        )
    else:
        raise FileNotFoundError(
            f"Frontend not found. Please run 'npm install && npm run build' in {_parent_dir / 'frontend'}"
        )


def st_copy_to_clipboard(
    text: str,
    label: str = "Copy to Clipboard",
    *,
    key: Optional[str] = None,
) -> None:
    """Render a button that copies *text* to the user's clipboard.

    Parameters
    ----------
    text : str
        The text to be copied to the clipboard when the user clicks the button.

    label : str, optional
        A human‑friendly label for the button (default is ``"Copy to Clipboard"``).

    key : str, optional
        A unique key for the component.  If you are using multiple copy
        buttons in the same app, supply a different key for each to
        ensure independent state.
    """
    # Invoke the component.  The return value will be either "success" or
    # "error" depending on whether the clipboard write succeeded on the
    # client side.
    result = _component_func(text=text, label=label, key=key)

    # Display feedback to the user if the component reports a result.
    if result == "success":
        st.success("Copied to clipboard!")
    elif result == "error":
        st.error("Failed to copy to clipboard.  Your browser may not support the clipboard API or the page may not be secure.")
