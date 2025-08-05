// This file implements the front-end for the Streamlit clipboard component.
// It is deliberately written as a small ES module with no external build
// tooling.  We import the Streamlit API from a CDN and use it to
// communicate with the Python backend.  When the user clicks the button
// the provided text is copied to the clipboard and a status string is
// returned via `Streamlit.setComponentValue`.

import { Streamlit } from 'https://cdn.jsdelivr.net/npm/streamlit-component-lib@2.0.0/dist/streamlit.js';

// Wait for the DOM to be fully loaded before executing.  This ensures the
// body and root container are available.
document.addEventListener('DOMContentLoaded', () => {
  // Tell Streamlit that the component is ready to receive messages.
  Streamlit.setComponentReady();
  // Set the initial frame height to fit our content.
  Streamlit.setFrameHeight();

  // Create the button element.  We'll update its label based on the
  // component's props.
  const button = document.createElement('button');
  button.id = 'copy-button';
  button.textContent = 'Copy to Clipboard';
  document.getElementById('root').appendChild(button);

  // Variables to hold the current text and label passed from Python.
  let clipboardText = '';
  let buttonLabel = 'Copy to Clipboard';

  // When the button is clicked, attempt to copy the text to the clipboard.
  button.addEventListener('click', async () => {
    // Use modern clipboard API if available.  This API requires a user
    // gesture (the click) and a secure context (HTTPS or localhost).
    const copySucceeded = async () => {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(clipboardText);
          return true;
        }
        return false;
      } catch (err) {
        return false;
      }
    };

    let success = await copySucceeded();

    // Fallback: use deprecated execCommand if available.  Some browsers
    // still support this API when running within iframes.
    if (!success) {
      const textarea = document.createElement('textarea');
      textarea.value = clipboardText;
      textarea.style.position = 'fixed'; // Prevent scrolling to bottom of page
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      try {
        success = document.execCommand('copy');
      } catch (err) {
        success = false;
      }
      document.body.removeChild(textarea);
    }

    // Provide visual feedback via the button label for a couple seconds.
    if (success) {
      const originalLabel = buttonLabel;
      button.textContent = '✅ Copied!';
      Streamlit.setComponentValue('success');
      setTimeout(() => {
        button.textContent = originalLabel;
      }, 2000);
    } else {
      const originalLabel = buttonLabel;
      button.textContent = '❌ Copy failed';
      Streamlit.setComponentValue('error');
      setTimeout(() => {
        button.textContent = originalLabel;
      }, 2000);
    }
  });

  // Listen for render events from Streamlit.  Each time the app reruns,
  // Streamlit will send updated props.  We update our internal state
  // accordingly.
  Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, (event) => {
    const args = event.detail.args || {};
    clipboardText = args.text || '';
    buttonLabel = args.label || 'Copy to Clipboard';
    button.textContent = buttonLabel;
    // Resize the iframe to fit our content whenever props change.
    Streamlit.setFrameHeight();
  });
});