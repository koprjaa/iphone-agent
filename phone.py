"""Controls an iPhone over WebDriverAgent on Wi-Fi.

A replacement for phone-harness in the EU, where iPhone Mirroring does not run.
The difference from phone-harness: WebDriverAgent returns an accessibility tree,
so the code taps a named element instead of a pixel guessed from OCR.

Setup: WebDriverAgent runs on the phone. Put its address in WDA_URL
(http://<ip>:8100).
"""
import os

import wda

URL = os.environ.get("WDA_URL") or "http://" + os.environ.get("PHONE_HOST", "127.0.0.1") + ":8100"
c = wda.Client(URL)
s = c.session()


def see(path="screen.png"):
    """Writes a screenshot to a file, for a vision model when a label is not enough."""
    c.screenshot(path)
    return path


def tree():
    """Returns the accessibility tree as JSON. This replaces the OCR in phone-harness."""
    return c.source(accessible=True)


def tap(label, timeout=5.0):
    """Taps an element by its label. Waits until the element appears."""
    s(label=label).get(timeout=timeout).tap()


def tap_text(text, timeout=5.0):
    s(text=text).get(timeout=timeout).tap()


def type_into(label, text, timeout=5.0):
    s(label=label).get(timeout=timeout).set_text(text)


def scroll(direction="up"):
    getattr(s, f"swipe_{direction}")()


def app(bundle_id):
    """Moves to an application, for example 'com.apple.Preferences'."""
    s.app_activate(bundle_id)


def here():
    """Returns what is in the foreground. Use it to verify an action."""
    return c.app_current()


def doctor():
    """Checks that WebDriverAgent answers and the session holds. Run it after install."""
    st = c.status()
    assert st.get("sessionId") or st.get("state"), f"WDA neodpovida: {st}"
    cur = here()
    assert "bundleId" in cur, f"session nedrzi: {cur}"
    print(f"OK  {URL}  popredi: {cur['bundleId']}")
    return True


if __name__ == "__main__":
    doctor()
