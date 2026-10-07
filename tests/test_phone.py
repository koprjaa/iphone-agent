import importlib

import pytest

import phone


@pytest.fixture(autouse=True)
def _reset_mocks():
    phone.c.reset_mock()
    phone.s.reset_mock()
    yield


def test_url_defaults_to_localhost_when_no_env_vars(monkeypatch):
    monkeypatch.delenv("WDA_URL", raising=False)
    monkeypatch.delenv("PHONE_HOST", raising=False)
    importlib.reload(phone)
    assert phone.URL == "http://127.0.0.1:8100"


def test_url_uses_phone_host_env_var(monkeypatch):
    monkeypatch.delenv("WDA_URL", raising=False)
    monkeypatch.setenv("PHONE_HOST", "192.168.1.50")
    importlib.reload(phone)
    assert phone.URL == "http://192.168.1.50:8100"


def test_url_prefers_wda_url_override(monkeypatch):
    monkeypatch.setenv("WDA_URL", "http://10.0.0.9:9999")
    monkeypatch.setenv("PHONE_HOST", "ignored-host")
    importlib.reload(phone)
    assert phone.URL == "http://10.0.0.9:9999"


def test_tap_builds_label_locator_and_taps():
    phone.tap("Login", timeout=3)
    phone.s.assert_called_once_with(label="Login")
    phone.s.return_value.get.assert_called_once_with(timeout=3)
    phone.s.return_value.get.return_value.tap.assert_called_once()


def test_tap_text_builds_text_locator_and_taps():
    phone.tap_text("Pokracovat")
    phone.s.assert_called_once_with(text="Pokracovat")
    phone.s.return_value.get.assert_called_once_with(timeout=5.0)
    phone.s.return_value.get.return_value.tap.assert_called_once()


def test_type_into_sets_text_on_located_element():
    phone.type_into("Username", "jan", timeout=2)
    phone.s.assert_called_once_with(label="Username")
    phone.s.return_value.get.assert_called_once_with(timeout=2)
    phone.s.return_value.get.return_value.set_text.assert_called_once_with("jan")


def test_scroll_dispatches_to_directional_swipe_method():
    phone.scroll("down")
    phone.s.swipe_down.assert_called_once()
    phone.s.reset_mock()
    phone.scroll()  # default direction is "up"
    phone.s.swipe_up.assert_called_once()


def test_app_activates_bundle_id():
    phone.app("com.apple.Preferences")
    phone.s.app_activate.assert_called_once_with("com.apple.Preferences")


def test_doctor_passes_when_session_and_foreground_present():
    phone.c.status.return_value = {"sessionId": "abc123"}
    phone.c.app_current.return_value = {"bundleId": "com.apple.MobileSafari"}
    assert phone.doctor() is True


def test_doctor_raises_when_session_missing():
    phone.c.status.return_value = {}
    phone.c.app_current.return_value = {"bundleId": "com.apple.MobileSafari"}
    with pytest.raises(AssertionError):
        phone.doctor()
