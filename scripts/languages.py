"""Build research/languages.json: the languages every user-facing Fontes text must exist in.

    uv run python scripts/languages.py

Reads Unicode CLDR supplemental data (territoryInfo, likelySubtags) and the language
autonyms from the cldr-json packages on jsDelivr, the registry's jurisdiction codes, and the
hand-written choices below. See research/languages.md for the method and the decisions.
"""
from __future__ import annotations

import json
from pathlib import Path

import httpx

from world_legal_mcp import registry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "languages.json"
CDN = "https://cdn.jsdelivr.net/npm"
CLDR_VERSION = "49.0.0"   # pinned so the file can be rebuilt exactly

# Registry codes that are not ISO 3166 territories, with the language(s) they work in.
# value: (territory for CLDR or None, working languages, basis)
SUPRANATIONAL = {
    "afchpr": (None, ["en", "fr", "ar", "pt-PT"],
               "African Court Rules of Court r. 18: the official languages of the African Union; "
               "in practice judgments appear in English and French, some in Arabic and Portuguese "
               "(unverified which are formal working languages)"),
    "ccj": (None, ["en"], "Caribbean Court of Justice sits in English"),
    "difc": ("AE", ["en"], "DIFC Courts proceed in English; the UAE's official language (ar) is added from CLDR"),
    "echr": (None, ["en", "fr"], "ECHR Rules of Court r. 34: official languages English and French"),
    "ecowas": (None, ["en", "fr", "pt-PT"], "ECOWAS Court: English, French and Portuguese"),
    "efta": (None, ["en"], "EFTA Court: language of the court is English"),
    "eu": (None, ["bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr", "hu", "it",
                  "lt", "lv", "mt", "nl", "pl", "pt-PT", "ro", "sk", "sl", "sv"],
           "CJEU: any of the 24 official EU languages can be the language of a case "
           "(Rules of Procedure art. 36); internal working language French"),
    "icj": (None, ["en", "fr"], "ICJ Statute art. 39: English and French"),
    "icsid": (None, ["en", "fr", "es"], "ICSID: English, French and Spanish"),
    "itlos": (None, ["en", "fr"], "ITLOS Statute art. 1 / Rules art. 43: English and French"),
    "us-states": ("US", [], "US state courts: CLDR's languages for the United States"),
    "untc": (None, ["ar", "zh-Hans", "en", "fr", "ru", "es"], "UN Treaty Collection: the six UN official languages"),
    "wto": (None, ["en", "fr", "es"], "WTO: English, French and Spanish"),
}
# Jurisdictions being built that are not in the registry yet.
PENDING = ["fr"]

# CLDR code -> UI locale code (BCP 47) Fontes uses for it.
UI_CODE = {"zh": "zh-Hans", "zh_Hant": "zh-Hant", "sr_Latn": "sr-Latn", "bs_Cyrl": "bs-Cyrl",
           "uz_Cyrl": "uz-Cyrl", "hak_Hant": "hak-Hant", "nan_Hant": "nan-Hant",
           "tzm": "zgh",   # Morocco's official Amazigh is written as Standard Moroccan Tamazight (IRCAM, Tifinagh)
           "no": "nb"}     # "no" is the macrolanguage; its written standards are nb and nn, both listed
# Portuguese: `pt` is written in the Brazilian norm; every other Portuguese-speaking territory
# (PT, AO, MZ, CV, GW, ST, TL...) and the supranational courts use the European norm, `pt-PT`.
PT_BRAZIL = "BR"
# CLDR official codes left out of the UI set: only when there is no written standard to translate into.
DROP = {
    "gsw": "Swiss German has no standard written form; Switzerland and Liechtenstein write Standard German (de).",
    "az_Cyrl": "Azerbaijan abandoned Cyrillic for Latin (1991 law, fully by 2001); nothing official is written in it now. az (Latin) covers it.",
}
# Autonyms CLDR 49 has no locale data for.
AUTONYM = {"ht": "Kreyòl ayisyen", "gn": "Avañe\u02bcẽ", "ay": "Aymar aru", "dv": "ދިވެހި",
           "nan-Hant": "臺灣台語", "hak-Hant": "臺灣客家語"}   # Taiwan Ministry of Education names
# Languages added although CLDR does not mark them official/de_facto_official for the territory.
ADD = {
    "iq": (["ckb"], "Iraq Constitution art. 4: Arabic and Kurdish are the two official languages; the iq "
                    "adapter covers the Kurdistan Region. CLDR marks ckb only official_regional."),
}
# Ethnologue total speakers (L1+L2, millions), as cited by Wikipedia's "List of languages by total
# number of speakers" (Ethnologue 2026, retrieved there 2026-03-08). Not checked against Ethnologue
# itself (paywalled). Only the rows we read are listed.
ETHNOLOGUE = {"en": 1493, "zh-Hans": 1183, "hi": 611, "es": 561, "ar": 335, "fr": 334, "bn": 274,
              "pt": 269, "id": 255, "ur": 246, "ru": 210, "de": 133, "ja": 126}
TOP10 = ["en", "zh-Hans", "hi", "es", "ar", "fr", "bn", "pt", "id", "ur"]
TIER1_EXTRA = ["tr", "pt-PT"]   # Turkish; European Portuguese as its own required file
RTL_SCRIPTS = {"Arab", "Hebr", "Thaa", "Syrc", "Nkoo", "Adlm"}


def fetch(path: str) -> dict:
    r = httpx.get(f"{CDN}/{path}", timeout=30, follow_redirects=True)
    r.raise_for_status()
    return r.json()


def main() -> None:
    ti = fetch(f"cldr-core@{CLDR_VERSION}/supplemental/territoryInfo.json")["supplemental"]
    assert ti["version"]["_cldrVersion"] == CLDR_VERSION.split(".")[0]
    terr = ti["territoryInfo"]
    likely = fetch(f"cldr-core@{CLDR_VERSION}/supplemental/likelySubtags.json")["supplemental"]["likelySubtags"]

    registry.discover()
    codes = sorted({c for c, j in registry._all.items() if not getattr(j, "via_lexifina", False)} | set(PENDING))
    jur: dict[str, dict] = {}
    dropped: list[dict] = []
    for code in codes:
        t, working, basis = SUPRANATIONAL.get(code, (code.upper(), [], "CLDR officialStatus"))
        langs = list(working)
        if t:
            for cl, v in terr[t].get("languagePopulation", {}).items():
                if v.get("_officialStatus") not in ("official", "de_facto_official"):
                    continue
                if cl in DROP:
                    dropped.append({"cldr": cl, "jurisdiction": code, "reason": DROP[cl]})
                    continue
                ui = UI_CODE.get(cl, cl)
                if ui == "pt" and t != PT_BRAZIL:
                    ui = "pt-PT"
                if ui not in langs:
                    langs.append(ui)
        extra, why = ADD.get(code, ([], ""))
        langs += [x for x in extra if x not in langs]
        jur[code] = {"languages": langs, "basis": basis + (f"; plus {', '.join(extra)}: {why}" if extra else ""),
                     **({"territory": t} if t else {}), **({"pending": True} if code in PENDING else {})}

    union = sorted({lang for j in jur.values() for lang in j["languages"]} | set(TOP10) | set(TIER1_EXTRA))

    def cldr_key(ui: str) -> str:
        return {v: k for k, v in UI_CODE.items()}.get(ui, ui.replace("-", "_"))

    def speakers(ui: str) -> int:
        """CLDR estimate: sum over territories of population x populationPercent (L1 and L2 where CLDR has them)."""
        keys = {cldr_key(ui)} | ({"no"} if ui == "nb" else set()) | ({"tzm"} if ui == "zgh" else set())
        if ui == "pt-PT":
            keys = {"pt"}
        total = 0.0
        for code, t in terr.items():
            if ui == "pt-PT" and code == PT_BRAZIL:
                continue
            lp = t.get("languagePopulation", {})
            pct = max((float(lp[k]["_populationPercent"]) for k in keys if k in lp), default=0.0)
            total += float(t["_population"]) * pct / 100
        return round(total)

    def script(ui: str) -> str:
        parts = ui.split("-")
        if len(parts) > 1 and len(parts[1]) == 4:
            return parts[1]
        return likely.get(parts[0], "und-Latn").split("-")[1]

    def lang_names(locale: str) -> dict:
        try:
            d = fetch(f"cldr-localenames-full@{CLDR_VERSION}/main/{locale}/languages.json")
        except httpx.HTTPError:
            return {}
        return d["main"][locale]["localeDisplayNames"]["languages"]

    en = lang_names("en")
    names = {}
    for ui in union:
        own = lang_names(ui)
        sub = ui.split("-")[1] if "-" in ui and ui not in en else ""
        names[ui] = ((en.get(ui) or en.get(ui.split("-")[0])) + (f" ({sub})" if sub else ""),
                     own.get(ui) or own.get(ui.split("-")[0]) or AUTONYM.get(ui))

    rows = []
    for ui in union:
        sc = script(ui)
        rows.append({
            "code": ui,
            "name": names[ui][0],
            "autonym": names[ui][1],
            "script": sc,
            "rtl": sc in RTL_SCRIPTS,
            "non_latin": sc != "Latn",
            "tier": 1 if ui in TOP10 or ui in TIER1_EXTRA else 2,
            "required": True,
            "top10_world": ui in TOP10,
            "cldr_speakers_estimate": speakers(ui),
            "ethnologue_2026_total_millions": ETHNOLOGUE.get(ui),
            "jurisdictions": [c for c, j in jur.items() if ui in j["languages"]],
        })
    rows.sort(key=lambda r: (r["tier"], -(r["ethnologue_2026_total_millions"] or 0), -r["cldr_speakers_estimate"]))
    for i, r in enumerate(sorted(rows, key=lambda r: -r["cldr_speakers_estimate"]), 1):
        r["cldr_rank"] = i

    out = {
        "generated_by": "scripts/languages.py",
        "source_language": "en",
        "sources": {
            "official_languages": f"Unicode CLDR {CLDR_VERSION.split('.')[0]} supplemental territoryInfo, "
                                  "officialStatus official or de_facto_official "
                                  f"({CDN}/cldr-core@{CLDR_VERSION}/supplemental/territoryInfo.json)",
            "scripts": f"Unicode CLDR {CLDR_VERSION.split('.')[0]} likelySubtags",
            "names": f"Unicode CLDR {CLDR_VERSION.split('.')[0]} localenames (English name, autonym)",
            "top10_world": "Ethnologue 2026 total speakers, as tabulated by Wikipedia 'List of languages by "
                           "total number of speakers' (retrieved there 2026-03-08). Unverified against "
                           "Ethnologue itself, which is paywalled. Russian (210 M) is 11th, behind Urdu.",
            "cldr_speakers_estimate": "sum over all CLDR territories of population x populationPercent; "
                                      "a rough L1+L2 estimate, used only to order tier 2",
        },
        "policy": "Every language listed is required. Tier only sets the order of work: tier 1 = the "
                  "10 most-spoken languages in the world (Ethnologue 2026) plus Turkish and European "
                  "Portuguese (pt = Brazilian, pt-PT = European); tier 2 = every other official or "
                  "working language of a covered jurisdiction.",
        "target": [r["code"] for r in rows],
        "tier1": [r["code"] for r in rows if r["tier"] == 1],
        "tier2": [r["code"] for r in rows if r["tier"] == 2],
        "rtl": [r["code"] for r in rows if r["rtl"]],
        "english_only": ["docs/ADAPTER_SPEC.md"],
        "languages": rows,
        "jurisdictions": jur,
        "dropped": dropped,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT}: {len(rows)} languages (tier 1: {len(out['tier1'])}, tier 2: {len(out['tier2'])}), "
          f"{len(dropped)} dropped")


if __name__ == "__main__":
    main()
