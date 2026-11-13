"""Translations: scripts/i18n_check.py on the repository and on small fixture folders."""
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import i18n_check  # noqa: E402
import i18n_docs  # noqa: E402

LANGS = json.loads((ROOT / "research" / "languages.json").read_text(encoding="utf-8"))
EN_UI = json.loads((ROOT / "installer" / "locales" / "en.json").read_text(encoding="utf-8"))
EN_DOCS = i18n_docs.labels("en")


def test_repository_translations_are_well_formed():
    r = i18n_check.check()
    assert r["errors"] == []
    assert r["target"] == LANGS["target"]
    assert "en" not in r["missing"]["installer"] and "tr" not in r["missing"]["installer"]


def test_language_list_policy():
    assert all(lang["required"] for lang in LANGS["languages"])
    n = len(LANGS["tier1"])
    assert set(LANGS["tier1"]) == set(LANGS["target"][:n]) and {"tr", "pt-PT"} <= set(LANGS["tier1"])
    assert len(LANGS["tier1"]) + len(LANGS["tier2"]) == len(LANGS["target"])
    for code in ("en", "zh-Hans", "hi", "es", "ar", "fr", "bn", "pt", "id", "ur"):
        assert code in LANGS["tier1"]
    rows = {lang["code"]: lang for lang in LANGS["languages"]}
    assert rows["pt"]["jurisdictions"] == ["br"] and "pt" in rows["pt-PT"]["jurisdictions"]
    rtl = {lang["code"] for lang in LANGS["languages"] if lang["rtl"]}
    assert {"ar", "he", "fa", "ur"} <= rtl and "tr" not in rtl


@pytest.fixture
def fixture(tmp_path):
    """A copy of the English sources plus one complete, valid Arabic translation."""
    loc, docs = tmp_path / "locales", tmp_path / "docs"
    loc.mkdir()
    shutil.copy(ROOT / "installer" / "locales" / "en.json", loc / "en.json")
    (docs / "en").mkdir(parents=True)
    shutil.copy(ROOT / "docs" / "i18n" / "en" / "strings.json", docs / "en" / "strings.json")
    (loc / "ar.json").write_text(json.dumps({k: v + " ar" for k, v in EN_UI.items()}), encoding="utf-8")
    ar = docs / "ar"
    ar.mkdir()
    notice = "ترجمة"
    (ar / "strings.json").write_text(json.dumps({**EN_DOCS, "doc_notice": notice}), encoding="utf-8")
    for name in ("INSTALL.md", "PRIVACY.md", "FAQ.md", "KEYS.md"):
        (ar / name).write_text(f"> {notice}\n\n# x\n", encoding="utf-8")
    (ar / "README.md").write_text(f"> {notice}\n\n" + "".join(
        f"<!-- {n}:start -->\n<!-- {n}:end -->\n" for n in ("languages", "coverage", "sources")), encoding="utf-8")
    (ar / "index.html").write_text(f'<!doctype html><html lang="ar" dir="rtl"><p>{notice}</p></html>',
                                   encoding="utf-8")
    return loc, docs


def _check(fixture):
    return i18n_check.check(*fixture, ROOT / "research" / "languages.json")


def test_valid_translation_passes_and_missing_languages_are_only_reported(fixture):
    r = _check(fixture)
    assert r["errors"] == []
    assert "ar" not in r["missing"]["installer"] and "ar" not in r["missing"]["docs"]
    assert "tr" in r["missing"]["installer"] and "zh-Hans" in r["missing"]["docs"]
    assert len(r["missing"]["docs"]) == len(LANGS["target"]) - 2


@pytest.mark.parametrize("change,message", [
    (lambda d: d.pop("fetch_ok"), "missing key 'fetch_ok'"),
    (lambda d: d.update(start="  "), "'start' is empty"),
    (lambda d: d.update(fetch_ok="{name} ok"), "placeholders"),
    (lambda d: d.update(start=3), "not a string"),
])
def test_malformed_locale_fails(fixture, change, message):
    f = fixture[0] / "ar.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    change(d)
    f.write_text(json.dumps(d), encoding="utf-8")
    assert any(message in e for e in _check(fixture)["errors"])


def test_key_english_no_longer_has_is_only_a_warning(fixture):
    f = fixture[0] / "ar.json"
    f.write_text(json.dumps({**json.loads(f.read_text(encoding="utf-8")), "extra": "x"}), encoding="utf-8")
    r = _check(fixture)
    assert r["errors"] == [] and any("unknown key 'extra'" in w for w in r["warnings"])


def test_unknown_language_code_fails(fixture):
    shutil.copy(fixture[0] / "ar.json", fixture[0] / "xx.json")
    assert any("'xx' is not a language" in e for e in _check(fixture)["errors"])


@pytest.mark.parametrize("damage,message", [
    (lambda ar: (ar / "PRIVACY.md").unlink(), "missing PRIVACY.md"),
    (lambda ar: (ar / "KEYS.md").unlink(), "missing KEYS.md"),
    (lambda ar: (ar / "FAQ.md").write_text("# x\n", encoding="utf-8"), "translation notice"),
    (lambda ar: (ar / "INSTALL.md").write_text("# x\n", encoding="utf-8"), "translation notice"),
    (lambda ar: (ar / "index.html").write_text('<html lang="ar"><p>ترجمة</p></html>', encoding="utf-8"),
     'dir="rtl"'),
    (lambda ar: (ar / "index.html").write_text('<html lang="en" dir="rtl"><p>ترجمة</p></html>',
                                               encoding="utf-8"), 'lang="ar"'),
    (lambda ar: (ar / "README.md").write_text("> ترجمة\n", encoding="utf-8"), "coverage:start/end"),
])
def test_malformed_docs_fail(fixture, damage, message):
    damage(fixture[1] / "ar")
    assert any(message in e for e in _check(fixture)["errors"])


def test_status_page_is_one_page_with_every_language(monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("status_page_i18n", ROOT / "scripts" / "status_page.py")
    sp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sp)
    tables = {"en": EN_DOCS, "ar": {**EN_DOCS, "status_title": "حالة", "status_source_other": "{n} مصادر"}}
    monkeypatch.setattr(sp.i18n_docs, "translations", lambda: ["ar"])
    monkeypatch.setattr(sp.i18n_docs, "_table", lambda lang: tables[lang])
    page = sp.render([{"checked_at": "2026-11-10T09:00:00+00:00", "fontes_version": "1",
                       "results": [{"jurisdiction": "at", "source": "C", "status": "ok", "detail": "",
                                   "checked_at": "2026-11-10T09:00:00+00:00"}]}])
    assert page.startswith("<!doctype html><html lang=en>")       # English without JavaScript
    data = json.loads(re.search(r"var S=(\{.*?\}),R=", page).group(1))
    assert data["ar"]["status_title"] == "حالة" and data["en"]["status_title"] == EN_DOCS["status_title"]
    assert 'R=["ar"]' in page and "data-i=status_banner_ok" in page and "data-p=status_source" in page
    assert "1 source" in page
