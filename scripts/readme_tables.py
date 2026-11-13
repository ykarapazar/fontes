"""Rebuild the two README tables from the adapters' metadata.

    uv run python scripts/readme_tables.py

Rewrites the text between <!-- coverage:start/end --> and <!-- sources:start/end --> in README.md
and in each translated docs/i18n/<lang>/README.md (headers and generated labels from that
language's strings.json; source names, hand-written cells and notes stay as they are).
Hand-written README text that the Source objects do not carry is kept in the
dicts below (seeded from the README as it stood on 2026-11-06).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from world_legal_mcp import registry
from world_legal_mcp.base import CASELAW, LEGISLATION

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n_docs  # noqa: E402

README = Path(__file__).resolve().parent.parent / "README.md"

# --- hand-written overrides -------------------------------------------------

# Code cell / jurisdiction name where the README says more than the adapter.
CODE_LABEL = {"gb": "`gb` (alias `uk`)"}
JUR_NAME: dict[str, str] = {'au': 'Australia (Commonwealth)',
 'ca': 'Canada (federal)',
 'ch': 'Switzerland (federal)',
 'difc': 'DIFC Courts (Dubai)',
 'icsid': 'ICSID (investment arbitration)',
 'us': 'United States (federal)'}
# (code, "caselaw" | "legislation") -> coverage cell, without the OFF marker.
COV_LABEL: dict[tuple[str, str], str] = {('ar', 'legislation'): 'InfoLEG (national laws)',
 ('at', 'caselaw'): 'RIS (OGH, VfGH, VwGH, BVwG, LVwG, DSB)',
 ('at', 'legislation'): 'RIS federal law',
 ('au', 'legislation'): 'Federal Register of Legislation',
 ('br', 'caselaw'): 'STF (Supreme Federal Court)',
 ('br', 'legislation'): 'normas.leg.br',
 ('ca', 'caselaw'): 'Supreme Court of Canada',
 ('ca', 'legislation'): 'Justice Laws',
 ('ch', 'caselaw'): 'Federal Supreme Court (bger.ch)',
 ('ch', 'legislation'): 'Fedlex (SR)',
 ('cl', 'legislation'): 'BCN Ley Chile',
 ('cn', 'caselaw'): "Supreme People's Court guiding cases",
 ('co', 'caselaw'): 'Corte Constitucional',
 ('cz', 'caselaw'): 'rozhodnuti.justice.cz (lower courts)',
 ('cz', 'legislation'): 'e-Sbírka',
 ('de', 'caselaw'): 'NeuRIS (federal courts, trial service)',
 ('de', 'legislation'): 'Gesetze im Internet',
 ('difc', 'caselaw'): 'DIFC Courts judgments',
 ('dk', 'legislation'): 'Retsinformation',
 ('echr', 'caselaw'): 'HUDOC',
 ('ee', 'legislation'): 'Riigi Teataja',
 ('efta', 'caselaw'): 'EFTA Court judgments',
 ('es', 'caselaw'): 'Constitutional Court only',
 ('es', 'legislation'): 'BOE consolidated law',
 ('eu', 'caselaw'): 'CELLAR (CJEU)',
 ('eu', 'legislation'): 'CELLAR (EUR-Lex)',
 ('fi', 'caselaw'): 'Finlex (KKO/KHO precedents)',
 ('fi', 'legislation'): 'Finlex open data',
 ('gb', 'caselaw'): 'Find Case Law (The National Archives, 2003 onward)',
 ('gb', 'legislation'): 'legislation.gov.uk',
 ('ge', 'caselaw'): 'Courts of Georgia (2018–2020)',
 ('ge', 'legislation'): 'Matsne',
 ('gr', 'caselaw'): 'Areios Pagos',
 ('gr', 'legislation'): 'Government Gazette (FEK)',
 ('hk', 'legislation'): 'Hong Kong e-Legislation (open data)',
 ('hr', 'caselaw'): 'Constitutional Court (in the gazette)',
 ('hr', 'legislation'): 'Narodne novine',
 ('hu', 'caselaw'): 'Bírósági Határozatok Gyűjteménye',
 ('icsid', 'caselaw'): 'ICSID case database',
 ('ie', 'legislation'): 'Irish Statute Book, LRC Revised Acts',
 ('il', 'legislation'): 'Knesset law database; Open Law Book (Wikisource, non-official)',
 ('in', 'legislation'): 'India Code',
 ('is', 'caselaw'): 'Ísland.is court rulings',
 ('it', 'legislation'): 'Normattiva',
 ('jp', 'legislation'): 'e-Gov 法令API',
 ('lu', 'legislation'): 'Legilux',
 ('lv', 'caselaw'): 'E-lietas (anonymised decisions)',
 ('ng', 'caselaw'): 'Supreme Court of Nigeria',
 ('nl', 'caselaw'): 'rechtspraak.nl',
 ('nl', 'legislation'): 'wetten.overheid.nl (BWB)',
 ('no', 'caselaw'): 'Supreme Court (official summaries only)',
 ('pl', 'caselaw'): 'Portal Orzeczeń (common courts)',
 ('pl', 'legislation'): 'Sejm ELI API',
 ('pt', 'caselaw'): 'DGSI, Tribunal Constitucional',
 ('pt', 'legislation'): 'PGDL (unofficial consolidations)',
 ('ro', 'caselaw'): 'ÎCCJ decision by id only (no search)',
 ('ro', 'legislation'): 'cdep.ro index search only (no text)',
 ('se', 'caselaw'): 'Rättspraxis (Domstolsverket)',
 ('se', 'legislation'): 'Riksdagen (SFS)',
 ('sg', 'caselaw'): 'SG Courts judgments',
 ('si', 'caselaw'): 'Sodna praksa',
 ('si', 'legislation'): 'PISRS',
 ('sk', 'caselaw'): 'Supreme Court',
 ('sk', 'legislation'): 'Slov-Lex',
 ('tr', 'caselaw'): 'Bedesten, Constitutional Court',
 ('tr', 'legislation'): 'Bedesten (mevzuat)',
 ('tw', 'caselaw'): 'Judicial Yuan (FJUD)',
 ('tw', 'legislation'): 'MOJ law texts by pcode (no search)',
 ('us', 'caselaw'): 'govinfo',
 ('us', 'legislation'): 'US Code (uscode.house.gov)',
 ('uy', 'caselaw'): 'BJN (Poder Judicial)',
 ('uy', 'legislation'): 'IMPO'}
# (code, index of the Source in adapter.sources) -> {column: text}
# columns: source, licence, commercial, ai, auth, rate, notes
CELL: dict[tuple[str, int], dict[str, str]] = {('ar', 0): {'notes': 'Credit "InfoLEG – Ministerio de Justicia de la Nación". Consolidated texts '
                      "are not official (only the Boletín Oficial is). **No case law: SAIJ's terms "
                      'allow personal use only, so it is not used.**',
             'source': 'InfoLEG (www.argentina.gob.ar/normativa, Ministerio de Justicia)'},
 ('at', 0): {'notes': 'robots.txt `Disallow: /` for all clients; officially documented open-data '
                      'API, read as a template rule (unconfirmed). **Anything beyond manual-scale '
                      'use must be announced to ris.it@bka.gv.at** and run 20:00–05:00 or '
                      'weekends.'},
 ('au', 0): {'notes': 'Undocumented site backend. www robots.txt: Crawl-delay 10; API host has '
                      'none.',
             'source': 'Federal Register of Legislation (api.prod.legislation.gov.au)'},
 ('br', 0): {'notes': 'No robots.txt. Undocumented internal API; may change without notice.'},
 ('br', 1): {'notes': "robots.txt allows all (legis.senado.leg.br's answers 403)."},
 ('ca', 0): {'commercial': 'Reasons: yes. Headnotes/editorial features: written permission',
             'notes': 'robots.txt blocks only one crawler (BUbiNG).'},
 ('ca', 1): {'notes': 'No robots.txt. Must not be presented as the official version.'},
 ('ch', 0): {'source': 'Federal Supreme Court (search.bger.ch)'},
 ('ch', 1): {'notes': '**fedlex.data.admin.ch robots.txt disallows `/filestore/*`**; we fetch the '
                      'same files from the www host, whose robots.txt allows them (what the Fedlex '
                      'viewer itself loads). Defensible, not confirmed with Fedlex.',
             'source': 'Fedlex (fedlex.data.admin.ch SPARQL + www.fedlex.admin.ch/filestore)'},
 ('cl', 0): {'notes': 'No robots.txt. No Ley Chile terms page found.',
             'source': 'BCN Ley Chile (www.leychile.cl, nuevo.leychile.cl)'},
 ('cn', 0): {'notes': 'No robots.txt. **No legislation: flk.npc.gov.cn robots.txt forbids all '
                      'automated access.** China Judgments Online needs a login and is not used.'},
 ('co', 0): {'notes': 'robots.txt allows /relatoria/ (full texts), disallows /API/ and '
                      '/sentencias/.'},
 ('co', 1): {'notes': 'Search matches metadata (number, magistrate, process), not judgment text. '
                      'Dataset updated monthly.',
             'source': 'datos.gov.co dataset of Corte Constitucional sentencias (Socrata)'},
 ('cz', 0): {'notes': 'No robots.txt. Lower courts only, from 2020.'},
 ('cz', 1): {'notes': 'No robots.txt. The REST backend is undocumented.'},
 ('de', 0): {'notes': 'robots.txt `Disallow: /` for all clients, but the API is documented for '
                      'building applications; same template reading as at/nl (unconfirmed). Still '
                      'a trial service. **Off by default — needs WLM_PERMITTED=de and the '
                      "operator's permission.**",
             'source': 'NeuRIS (testphase.rechtsinformationen.bund.de)'},
 ('difc', 0): {'notes': 'robots.txt disallows only /menu and /videos. **Off by default — needs '
                        "WLM_PERMITTED=difc and the operator's permission.**",
               'source': 'DIFC Courts judgments (www.difccourts.ae)'},
 ('dk', 0): {'notes': "Search uses the website's undocumented JSON. **Case law not covered: "
                      'Domsdatabasen only allows API access after an approved application**, so it '
                      'is not used.'},
 ('echr', 0): {'notes': "No robots.txt. A commercial deployment needs the Court's permission."},
 ('ee', 0): {'notes': 'robots.txt disallows ~5,600 listed acts (we refuse those) and the '
                      'court-decision routes, so **no case law**.'},
 ('efta', 0): {'notes': 'api.eftacourt.int robots.txt allows all; eftacourt.int has none.'},
 ('es', 0): {'notes': 'robots.txt has no Crawl-delay.',
             'source': 'BOE consolidated law (www.boe.es)'},
 ('es', 1): {'notes': 'robots.txt 404.',
             'source': 'Constitutional Court HJ (hj.tribunalconstitucional.es)'},
 ('eu', 0): {'commercial': 'Yes (unconfirmed for CJEU material)',
             'notes': 'Allowed by robots.txt. Acknowledge the source; do not distort.'},
 ('fi', 0): {'source': 'Finlex open data (opendata.finlex.fi)'},
 ('gb', 0): {'ai': '**No** (robots.txt blocks named AI bots: GPTBot, ClaudeBot…)',
             'notes': 'Our User-Agent is not blocked. **Computational analysis needs the free '
                      'licence from caselaw@nationalarchives.gov.uk — get it before hosting.** '
                      'Coverage from 2003.'},
 ('gb', 1): {'notes': 'robots.txt: Crawl-delay 5.'},
 ('ge', 0): {'notes': 'Supreme Court search (supremecourt.ge) is robots-disallowed and not used.'},
 ('ge', 1): {'notes': 'Decisions dated 2018-01 to 2020-04 only.',
             'source': 'Courts of Georgia decisions (ecd.court.ge)'},
 ('gr', 0): {'notes': 'Supreme Civil and Criminal Court only.',
             'source': 'Areios Pagos case law (www.areiospagos.gr)'},
 ('gr', 1): {'licence': 'Terms of use: personal, informational, non-commercial use only; no '
                        'reproduction or copying for non-personal use without permission',
             'notes': "**Off by default — needs WLM_PERMITTED=gr and the operator's permission.** "
                      "Scanned FEK issues have no text layer and are reported, not OCR'd.",
             'source': 'Government Gazette search (search.et.gr, Εθνικό Τυπογραφείο)'},
 ('hk', 0): {'notes': 'Attribute the HKSAR Government, DoJ and DATA.GOV.HK. Open-data XML, not the '
                      "verified copies with legal status. **No case law: the Judiciary's Legal "
                      'Reference System and HKLII both forbid automated access in robots.txt.** '
                      'www.elegislation.gov.hk itself is robots-disallowed.'},
 ('hr', 0): {'notes': 'robots.txt disallows ~100 gazette articles by path (checked before each '
                      'fetch) and searches of the notices part (not used). Case law = '
                      'Constitutional Court decisions published in the gazette only: '
                      'odluke.sudovi.hr and sljeme.usud.hr are `Disallow: /`.'},
 ('hu', 0): {'notes': 'Case law only, PDF full texts. **No legislation: the Nemzeti '
                      "Jogszabálytár's terms forbid automated requests without written "
                      'permission.**'},
 ('icsid', 0): {'notes': 'robots.txt allows /api and case pages. Text-layer PDFs only (no OCR).'},
 ('ie', 0): {'notes': "robots.txt 404. Search uses the site's undocumented Solr index. **No case "
                      'law: judgments.courts.ie robots.txt is `Disallow: /`.**'},
 ('ie', 1): {'notes': 'robots.txt allows all. Attribute the Oireachtas and the LRC separately.'},
 ('il', 0): {'notes': 'Official law index and metadata.'},
 ('il', 1): {'notes': 'Volunteer-maintained consolidated text (shown as a warning); check the '
                      'Knesset gazette before relying on it. No case law.'},
 ('in', 0): {'notes': 'robots.txt returns HTTP 500. **Off by default — needs WLM_PERMITTED=in and '
                      "the operator's permission.** Whether the Copyright Act 1957 overrides this "
                      'for the Acts is unverified.'},
 ('is', 0): {'notes': 'No robots.txt. Undocumented GraphQL backend of the portal.'},
 ('it', 0): {'source': 'Normattiva open data (dati/api.normattiva.it)'},
 ('lu', 0): {'notes': 'data.legilux.public.lu robots.txt disallows /eli/* and /filestore/*; files '
                      'are read from legilux.public.lu, whose robots.txt allows them.',
             'source': 'Legilux (legilux.public.lu, data.legilux.public.lu)'},
 ('lv', 0): {'notes': 'No robots.txt. Anonymised decisions. **No legislation: likumi.lv search is '
                      "robots-disallowed and re-use needs Latvijas Vēstnesis' written consent.**",
             'source': 'E-lietas portāls (gateway.elieta.lv, Tiesu administrācija)'},
 ('ng', 0): {'notes': 'Supreme Court judgments only. No legislation.'},
 ('nl', 0): {'notes': 'Allowed (PDF download path excluded; not used).',
             'source': 'rechtspraak.nl (uitspraken.rechtspraak.nl, data.rechtspraak.nl)'},
 ('nl', 1): {'rate': 'Unpublished fair-use policy; 1 s spacing',
             'ai': '**No** (wetten.overheid.nl blocks AI agents by name; we only link to it)',
             'notes': 'robots.txt `Disallow: /` for all clients. Officially documented developer '
                      'API ("Handleiding SRU BWB"/"SRU 2.0"); we read the blanket rule as a '
                      "template on KOOP's API hosts (unconfirmed). One search per question, ≤50 "
                      'records. Contact: cup@koop.overheid.nl.',
             'source': 'BWB legislation search (zoekservice.overheid.nl, SRU)'},
 ('no', 0): {'notes': '**Summaries only:** the full-judgment PDFs are under a robots-disallowed '
                      'path. **No legislation and no lower courts: lovdata.no and api.lovdata.no '
                      'robots.txt are `Disallow: /`.**',
             'source': 'domstol.no Supreme Court decision pages (Domstoladministrasjonen)'},
 ('pl', 0): {'notes': 'Has a CAPTCHA bot check (not triggered in testing).'},
 ('pl', 1): {'notes': 'No robots.txt (WAF rejects the path).'},
 ('pt', 0): {'notes': 'robots.txt 404. Occasional empty replies.'},
 ('pt', 1): {'notes': 'robots.txt empty.'},
 ('pt', 2): {'notes': 'robots.txt 404. **Unofficial consolidations; ask PGDL before systematic or '
                      'commercial reuse** (shown as a warning).'},
 ('ro', 0): {'notes': '**Decision by id only:** search results come from a robots-disallowed path. '
                      'iccj.ro, ccr.ro and ReJust sit behind bot checks and are not used.',
             'source': 'ÎCCJ decisions (www.scj.ro)'},
 ('ro', 1): {'notes': "Index search, no text ('nu au caracter oficial'). legislatie.just.ro was "
                      'down when tested (2026-11-05).',
             'source': 'Chamber of Deputies legislative database (www.cdep.ro), metadata only'},
 ('se', 0): {'notes': 'Documented OpenAPI.'},
 ('se', 1): {'notes': 'Must not suggest the Riksdag stands behind the service.',
             'source': 'Riksdagen open data (data.riksdagen.se)'},
 ('sg', 0): {'licence': '© Government of Singapore; eLitigation Terms of Use cl. 6.1: no '
                        "reproduction or display without CrimsonLogic's prior written approval; "
                        'Judiciary terms: no commercial reuse without permission',
             'notes': "**Off by default — needs WLM_PERMITTED=sg and the operator's permission.** "
                      "No legislation: Singapore Statutes Online blocks this project's User-Agent "
                      '(403) and puts automated extraction under extra conditions.',
             'source': 'SG Courts judgments (www.elitigation.sg/gd)'},
 ('si', 0): {'source': 'Sodna praksa (www.sodnapraksa.si)'},
 ('si', 1): {'notes': 'robots.txt disallows only the /iskanje UI route, not /api. A 403 triggers a '
                      'proof-of-work bot check, which we do not solve. Unofficial consolidations.'},
 ('sk', 0): {'notes': 'Supreme Court only: obcan.justice.sk robots.txt disallows /pilot, so lower '
                      'courts are not covered.'},
 ('sk', 1): {'notes': 'Undocumented search API behind the SPA.'},
 ('tr', 0): {'notes': 'Undocumented public-site API.',
             'source': 'Bedesten (bedesten.adalet.gov.tr)'},
 ('tr', 1): {'source': 'Constitutional Court decision banks (*.anayasa.gov.tr)'},
 ('tw', 0): {'notes': 'Traditional Chinese; ROC dates converted.'},
 ('tw', 1): {'notes': 'robots.txt is `Disallow: /` except LawAll.aspx, so **no legislation '
                      'search**: laws open by pcode (B0000001 = 民法).'},
 ('us', 0): {'auth': '**Search needs a free api.data.gov key** (`WLM_US_GOVINFO_KEY`, set in the '
                     'environment or a `.env` file); falls back to `DEMO_KEY`. Fetching needs none',
             'notes': 'A shared deployment must set its own key.',
             'source': 'govinfo (api.govinfo.gov, www.govinfo.gov)'},
 ('us', 1): {'notes': 'Its search endpoints return 403 (Akamai) and are not used.'},
 ('uy', 0): {'notes': "robots.txt disallows /cgi-bin/ (IMPO's search), so laws are found by code "
                      "name or number only. **Get IMPO's confirmation before redistributing or "
                      'commercial use** (shown as a warning).'},
 ('uy', 1): {'notes': 'No robots.txt.'}}
# Rows with no Source object of their own, inserted after (code, index).
EXTRA_ROWS: dict[tuple[str, int], list[str]] = {('nl', 1): ['| nl | BWB law texts (repository.officiele-overheidspublicaties.nl) | CC0 | Yes | '
             '(as above) | None | Unknown; 1 s spacing | No robots.txt. |']}

# --- generation -------------------------------------------------------------


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


def _status(j, methods) -> str:
    have = [m for m in methods if j.supports(m)]
    return "full" if len(have) == len(methods) else ("partial" if have else "none")


def coverage_rows(L: dict[str, str] | None = None) -> list[str]:
    L = L or i18n_docs.labels()
    rows = ["| " + " | ".join(L[f"readme_col_{c}"] for c in ("code", "jurisdiction", "caselaw", "legislation"))
            + " |", "|---|---|---|---|"]
    for j in registry.available():
        cells = []
        for kind, methods in (("caselaw", CASELAW), ("legislation", LEGISLATION)):
            status = _status(j, methods)
            if status == "none":
                cells.append(None)
                continue
            srcs = [s for s in j.sources if kind in s.covers]
            label = COV_LABEL.get((j.code, kind)) or ", ".join(s.name for s in srcs)
            if status == "partial" and (j.code, kind) not in COV_LABEL:
                label += " " + L["readme_partial"]
            if any(s.needs_permission for s in srcs):
                label += " " + L["readme_off"]
            cells.append(label)
        if cells == [None, None]:
            continue
        rows.append("| " + " | ".join([
            CODE_LABEL.get(j.code, f"`{j.code}`"),
            _cell(JUR_NAME.get(j.code, j.name)),
            *(_cell(c) if c else "—" for c in cells)]) + " |")
    return rows


def _yes_no(v, unknown: str, L: dict[str, str]) -> str:
    return {True: L["readme_yes"], False: L["readme_no"], None: unknown}[v]


def generated_cells(j, s, L: dict[str, str] | None = None) -> dict[str, str]:
    L = L or i18n_docs.labels()
    host = urlparse(s.url).netloc
    return {
        "source": s.name if host.removeprefix("www.") in s.name else f"{s.name} ({host})",
        "licence": _cap(s.licence) or L["readme_not_stated"],
        "commercial": _yes_no(s.commercial_use, L["readme_unknown"], L),
        "ai": _yes_no(s.ai_use, L["readme_not_stated"], L),
        "auth": L["readme_none"] if s.auth == "none" else _cap(s.auth),
        "rate": _cap(s.rate_limit) or L["readme_unknown"],
        "notes": s.warning,
    }


COLS = ("source", "licence", "commercial", "ai", "auth", "rate", "notes")


def source_rows(L: dict[str, str] | None = None) -> list[str]:
    L = L or i18n_docs.labels()
    rows = ["| " + " | ".join(L[f"readme_col_{c}"] for c in ("country",) + COLS) + " |",
            "|---|---|---|---|---|---|---|---|"]
    for j in registry.available():
        for i, s in enumerate(j.sources):
            c = generated_cells(j, s, L) | CELL.get((j.code, i), {})
            if s.needs_permission and "WLM_PERMITTED" not in c["notes"]:
                c["notes"] = c["notes"] + " " + L["readme_off_note"].format(code=j.code)
            rows.append("| " + " | ".join([j.code, *(_cell(c[k]) for k in COLS)]) + " |")
            rows.extend(EXTRA_ROWS.get((j.code, i), []))
    return rows


def replace_block(text: str, name: str, rows: list[str]) -> str:
    pat = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"README.md has no <!-- {name}:start/end --> markers")
    return pat.sub(lambda m: m.group(1) + "\n".join(rows) + m.group(2), text)


def main() -> None:
    text = README.read_text()
    text = replace_block(text, "coverage", coverage_rows())
    text = replace_block(text, "sources", source_rows())
    README.write_text(text)
    print(f"coverage: {len(coverage_rows()) - 2} rows, sources: {len(source_rows()) - 2} rows")
    for lang in i18n_docs.translations():
        path = i18n_docs.I18N / lang / "README.md"
        if not path.exists():
            continue
        L = i18n_docs.labels(lang)
        text = path.read_text(encoding="utf-8")
        for name, rows in (("coverage", coverage_rows(L)), ("sources", source_rows(L))):
            text = i18n_docs.replace_block(text, name, "\n".join(rows)) or text
        path.write_text(text, encoding="utf-8")
        print(f"updated {path.relative_to(README.parent)}")


if __name__ == "__main__":
    main()
