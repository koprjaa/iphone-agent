"""Shared test setup.

phone.py creates a WebDriverAgent client and session at import time
(`c = wda.Client(URL); s = c.session()`), so the `wda` package is replaced
with a MagicMock-based fake *before* phone.py is ever imported. No test here
talks to a real phone, a real WebDriverAgent server, or the network.
"""
import socket
import sys
import types
from unittest.mock import MagicMock

import pytest

_fake_wda = types.ModuleType("wda")
_fake_wda.Client = MagicMock(name="wda.Client")
sys.modules["wda"] = _fake_wda


@pytest.fixture(autouse=True)
def _bez_site(monkeypatch):
    def zakazano(*args, **kwargs):
        raise RuntimeError("testy nesmí na síť")

    monkeypatch.setattr(socket.socket, "connect", zakazano)
