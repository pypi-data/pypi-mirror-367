# Streamlit Contrib Clipboard

`streamlit-contrib-clipboard` is a lightweight Streamlit component that lets your app copy arbitrary text to the user’s clipboard.  Unlike many existing approaches which silently fail when your app is embedded in an iframe (for example on Streamlit Community Cloud), this component uses modern clipboard APIs with sensible fall‑backs so it works reliably.

## Installation

Install the package via pip.  You’ll need Python 3.8 or newer and Streamlit 1.20 or higher:

```bash
pip install streamlit-contrib-clipboard
```

## Usage

Import the component and call `st_copy_to_clipboard` anywhere in your Streamlit app.  Pass the text you want copied along with an optional label for the button.

```python
from streamlit_contrib_clipboard import st_copy_to_clipboard

# Copy a simple message
st_copy_to_clipboard("Hello, World!", label="Copy Greeting")

# Copy the current timestamp
import datetime
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st_copy_to_clipboard(timestamp, label="📋 Copy Timestamp")
```

When the user clicks the button the provided text is copied to their clipboard.  A short success message is displayed when the copy succeeds, and an error is shown when the browser denies clipboard access (for example on non‑HTTPS pages or older browsers).

## Features

- ✅ **Works inside iframes** – uses the modern `navigator.clipboard.writeText()` API with fall‑backs to ensure copy operations work even when your Streamlit app is embedded in another page.
- 🔒 **Secure contexts** – gracefully degrades when running over plain HTTP or in unsupported browsers.
- 🚀 **Simple API** – just call `st_copy_to_clipboard(text, label)` from your app.
- 💬 **Visual feedback** – optional toast messages inform the user when copy succeeds or fails.

## Limitations

- Clipboard write access requires a user gesture (button click).  The component cannot automatically copy text without interaction.
- The component must run in a secure context (HTTPS or localhost).  On insecure pages the copy operation will be blocked.
- Older browsers may only support the fall‑back strategy which uses `document.execCommand()`; this approach is deprecated and may fail in sandboxed iframes.

## Demo

This repository includes a small demo application in the `demo/` directory.  You can run it locally with:

```bash
streamlit run demo/app.py
```

On Streamlit Community Cloud the component works even though your app is embedded in an iframe.

## Development

The component is implemented as a custom Streamlit component with a React front‑end.  The front‑end lives in `streamlit_contrib_clipboard/frontend`.  After making changes to the JavaScript, run `npm install` and `npm run build` in that directory, then re‑run your Streamlit app to load the updated component.

## License

This project is licensed under the MIT License – see the `LICENSE` file for details.
