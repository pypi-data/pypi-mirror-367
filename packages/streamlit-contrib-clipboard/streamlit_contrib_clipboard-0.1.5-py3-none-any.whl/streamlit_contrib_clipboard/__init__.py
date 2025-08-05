"""
streamlit_contrib_clipboard
===========================

This package exposes a helper function for copying text to the clipboard
from within Streamlit apps.  It wraps a small custom component built
in React which uses the modern clipboard API and fall‑backs to work
reliably even when your app runs inside an iframe (such as on Streamlit
Community Cloud).

Example usage:

    from streamlit_contrib_clipboard import st_copy_to_clipboard
    st_copy_to_clipboard("Hello, World!", label="Copy greeting")

See the README for more details.
"""

from .copy_to_clipboard import st_copy_to_clipboard  # noqa: F401

__all__ = [
    "st_copy_to_clipboard",
]
