"""Ovládání iPhonu přes WebDriverAgent po Wi-Fi.

Náhrada phone-harness pro EU, kde iPhone Mirroring není.
Rozdíl proti phone-harness: WDA vrací accessibility tree, takže se
neklikají nahádané pixely z OCR, ale konkrétní prvky podle labelu.

Setup: WDA běží na telefonu, adresa v env WDA_URL (http://<ip>:8100).
"""
import os
import wda

URL = os.environ.get("WDA_URL") or "http://" + os.environ.get("PHONE_HOST", "127.0.0.1") + ":8100"
c = wda.Client(URL)
s = c.session()


def see(path="screen.png"):
    """Screenshot do souboru. Pro vision model, když label nestačí."""
    c.screenshot(path)
    return path


def tree():
    """Accessibility tree jako JSON. Tohle nahrazuje OCR z phone-harness."""
    return c.source(accessible=True)


def tap(label, timeout=5.0):
    """Klik na prvek podle labelu. Čeká, až se objeví."""
    s(label=label).get(timeout=timeout).tap()


def tap_text(text, timeout=5.0):
    s(text=text).get(timeout=timeout).tap()


def type_into(label, text, timeout=5.0):
    s(label=label).get(timeout=timeout).set_text(text)


def scroll(direction="up"):
    getattr(s, f"swipe_{direction}")()


def app(bundle_id):
    """Přepne na appku, např. 'com.apple.Preferences'."""
    s.app_activate(bundle_id)


def here():
    """Co je teď v popředí. Verifikace po akci."""
    return c.app_current()


def doctor():
    """Ověří, že WDA odpovídá a session drží. Spusť po instalaci WDA."""
    st = c.status()
    assert st.get("sessionId") or st.get("state"), f"WDA neodpovida: {st}"
    cur = here()
    assert "bundleId" in cur, f"session nedrzi: {cur}"
    print(f"OK  {URL}  popredi: {cur['bundleId']}")
    return True


if __name__ == "__main__":
    doctor()
