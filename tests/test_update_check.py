"""The in-server update notice, offline: PyPI is replaced by a fake response."""
import json
import time

import pytest

from world_legal_mcp import update_check as uc


class FakeResponse:
    def __init__(self, status, payload):
        self.status_code, self._payload = status, payload

    def json(self):
        return self._payload


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTES_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("FONTES_NO_UPDATE_CHECK", raising=False)
    monkeypatch.setattr(uc, "_started", False)
    return tmp_path / "update-check.json"


def test_refresh_caches_latest_and_notice_shows_it(cache):
    seen = []
    uc.refresh(get=lambda url, timeout: seen.append(url) or FakeResponse(200, {"info": {"version": "0.3.0"}}))
    assert seen == ["https://pypi.org/pypi/fontes-mcp/json"]
    assert json.loads(cache.read_text())["latest"] == "0.3.0"
    assert "Fontes 0.3.0 is available (this is 0.2.9)" in uc.notice("0.2.9")
    assert uc.notice("0.3.0") == "" and uc.notice("0.10.0") == ""


def test_errors_are_cached_without_notice(cache):
    uc.refresh(get=lambda url, timeout: FakeResponse(404, {}))
    assert json.loads(cache.read_text())["latest"] is None
    def boom(url, timeout):
        raise OSError("offline")
    uc.refresh(get=boom)
    assert uc.notice("0.1.0") == ""


def test_stale_cache_refreshes_in_background_once(cache, monkeypatch):
    calls = []
    monkeypatch.setattr(uc, "refresh", lambda: calls.append(1))
    cache.write_text(json.dumps({"checked": time.time() - 2 * uc.CHECK_EVERY, "latest": "9.0"}))
    assert "9.0" in uc.notice("1.0")   # old answer shown right away, no waiting
    uc.notice("1.0")
    time.sleep(0.1)
    assert calls == [1]                # one background refresh per process


def test_fresh_cache_does_not_refresh(cache, monkeypatch):
    monkeypatch.setattr(uc, "refresh", lambda: pytest.fail("should not refresh"))
    cache.write_text(json.dumps({"checked": time.time(), "latest": "0.1.0"}))
    assert uc.notice("0.1.0") == ""


def test_switch_off(cache, monkeypatch):
    cache.write_text(json.dumps({"checked": time.time(), "latest": "9.0"}))
    monkeypatch.setenv("FONTES_NO_UPDATE_CHECK", "1")
    assert uc.notice("1.0") == ""
