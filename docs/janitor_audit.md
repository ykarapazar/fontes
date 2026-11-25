# Janitor audit

Goal: every module scores 5 on T C E F M S (tests also N, Fn), with behaviour unchanged.
Anchors: 5 = a careful reviewer would change nothing; 4 = a few small items; 3 = clear items one pass
would fix; 2 = hard to change safely; 1 = unreadable or broken. T Tidy, C Compact, E Elegant,
F Future-proof, M Modular, S AI slop; for tests N Needed (catches a regression a user would feel, not
covered elsewhere) and Fn Functional (fails when the code it covers breaks).

Gate for behaviour-neutral rounds: `uv run pytest -q tests --ignore=tests/live` green (baseline 960
passed), plus `uv run pytest tests/live -k <code>` for touched adapters without offline tests
(difc, gt, hk, jo), plus a blind re-score of the touched modules.

## Summary (baseline)

| group | modules | T | C | E | F | M | S | all 5 |
|---|---|---|---|---|---|---|---|---|
| Core package and config | 29 | 4.1 | 4.7 | 4.4 | 4.2 | 4.4 | 4.4 | 8 |
| Adapters | 125 | 3.5 | 3.2 | 3.2 | 3.1 | 3.3 | 3.8 | 1 |
| Scripts, installers, relay | 32 | 3.8 | 3.7 | 3.9 | 3.5 | 3.9 | 4.2 | 1 |
| Docs (hand-written) | 24 | 3.7 | 3.7 | 4.1 | 3.5 | 4.2 | 4.2 | 2 |
| Offline tests | 18 rows (152 files) | 3.2 | 3.4 | 3.3 | 3.8 | 3.6 | 3.6 | 0 |
| Live tests | 7 rows (127 files) | 3.6 | 4.0 | 4.1 | 3.3 | 3.9 | 4.0 | 1 |

Baseline 2026-11-23: blind scorers (fresh context, anchors and file list only, read-only). Test files
are scored as families with outliers on their own rows. Scorer line numbers in adapters_5 (py..tm) and
the live-test family were not all re-checked by the scorer; verify before acting.

## Scores

### Core package and config

| module | T | C | E | F | M | S | biggest concrete issue / cheapest fix |
|---|---|---|---|---|---|---|---|
| src/world_legal_mcp/__init__.py | 3 | 5 | 5 | 3 | 5 | 5 | `__version__` (line 2) has no readers (grep finds none) and is a 6th hand-kept copy of the version. Delete it. |
| src/world_legal_mcp/_http.py | 4 | 4 | 4 | 4 | 4 | 3 | Docstring :5-9 has two overlapping "Checked 2026-11-10 / 2026-11-05" lines and a history note ("nl-legal-mcp once found blocking"); keep one. `localname` (:179) has no `_http.` caller (only gb.py imports it by name, fine). `_fetch` imports SourceError inside the function (:107) with no comment on the cycle. Fix: trim docstring to current facts. |
| src/world_legal_mcp/base.py | 4 | 5 | 4 | 4 | 4 | 4 | Docstring line 11 writes `Results[DecisionHit]` but models.Results is not generic; line 82 cites `us-ca` as a code example although no adapter code has a hyphen (longest is 6 letters, all alphabetic). `kind_of` (115) is duplicated by `server._KIND` (server.py:41). Fix the two comments. |
| src/world_legal_mcp/bugreport.py | 4 | 4 | 4 | 4 | 4 | 4 | Report directory comes from `update_check.cache_file().parent` (39), and stats.py:51 does the same: cache-dir resolution lives in a module named for one of its three users. `t("bug_ask_dialog")` is used both as the field description (114) and the elicit message (123), so the dialog says it twice. Move `cache_dir()` to a shared spot. |
| src/world_legal_mcp/health.py | 3 | 4 | 3 | 3 | 3 | 3 | Two jobs: offline script logic and the runtime `notices()` used by the server (docstring 1-11). `markdown()` (224-246) embeds maintainer ops text (launchd commands, a person's `~/Library` paths) in a generated report, and says `status/HEALTH.md` (written by health_daily.sh:13) while the report itself lives at docs/HEALTH.md. Move that prose to a doc, keep the table. Magic 15000 vs 20000 (95, 100). |
| src/world_legal_mcp/i18n.py | 5 | 5 | 4 | 5 | 4 | 5 | Load-by-path fallback (16-19) is an accepted packaging cost, documented. Nothing to change. |
| src/world_legal_mcp/intermediates.pem | 5 | 5 | 5 | 5 | 5 | 5 | 5 certs, all valid until 2028-09 or later; each block names its host and source URL. Nothing to change. |
| src/world_legal_mcp/models.py | 5 | 5 | 4 | 4 | 5 | 4 | `Results.items: list` (98) is untyped while base.py documents `Results[DecisionHit]`. Make it generic or fix the base docstring. |
| src/world_legal_mcp/registry.py | 4 | 5 | 4 | 5 | 4 | 5 | `server._resolve` reads private `registry._broken` (server.py:81). Add a public `why_broken(code)`. |
| src/world_legal_mcp/render.py | 3 | 3 | 3 | 3 | 4 | 4 | `toc()` (138-191) is 55 lines: folding lambdas, three-tier matching, entry listing and fallback text in one function, and the entry-line format is written twice (174-175, 186-187). `caselaw_results` / `legislation_results` (80-135) repeat the same frame. Hardcoded 40000 and 30 (138, 185). Split the keyword filter and an `_entry_line` helper out. |
| src/world_legal_mcp/server.py | 3 | 3 | 3 | 3 | 3 | 3 | 523 lines, five jobs: dispatch, filter/date validation (94-141), a 75-line `list_jurisdictions` renderer (214-287), tool defs, and a pydantic internals patch (466-489). `_check_dates` decides calendar from regex over a filter's description text (130 `Bikram / Sambat / Hijri / ...`), which is data hiding in prose. `"too large" not in msg` (174) couples to wording in `_http._fetch` (113). `_BETA` + update-notice prepend is duplicated (239-241, 284-286). Comment 466 is history ("used to be dropped silently"). `_KIND` (41) duplicates `kind_of`. Move validation and list rendering out; carry an explicit flag on SourceError instead of matching text. |
| src/world_legal_mcp/stats.py | 4 | 4 | 4 | 4 | 4 | 4 | `_today()` (68) and the inline strftime at 108 repeat what `_http.today()` / bugreport.py:57 do three ways. Docstring line 8 "RELAY_URL, or FONTES_RELAY to override" is accurate but wordy. Minor. |
| src/world_legal_mcp/update_check.py | 4 | 5 | 4 | 4 | 3 | 4 | `cache_file()` (27-36) is the cache-dir resolver for stats.py and bugreport.py too, under an update-check name. Same fix as bugreport. |
| pyproject.toml | 4 | 5 | 4 | 3 | 5 | 4 | Version is hand-copied into 6 files (pyproject:3, `__init__`:2, server.json:6 and :17, plugin.json:4, plugin/.mcp.json:6, plugin/README.md:6); only plugin_bundle.py checks some, nothing checks server.json. Classifier "3 - Alpha" (18) vs `_BETA` text "Fontes is in beta" (server.py:209). `mcp[cli]` (21): nothing imports mcp.cli or typer (grep), so the `cli` extra looks unneeded. |
| Dockerfile | 5 | 5 | 5 | 5 | 5 | 5 | Copies exactly what the wheel build needs (matches pyproject force-include); comments carry information. |
| .dockerignore | 3 | 5 | 5 | 5 | 5 | 5 | Lists paths that do not exist in the repo: `launch`, `status`, `.worktrees`, `.claude` (ls confirms). Drop them. |
| .gitignore | 4 | 5 | 5 | 5 | 5 | 4 | Lines 13-15 name a local-only third-party skill set by author/licence; fine, but `/status/` (10) is the local copy written by health_daily.sh, which is not stated. |
| server.json | 4 | 5 | 5 | 3 | 5 | 5 | Version twice (6, 17), unchecked by any script. Omits optional `WLM_FR_PISTE_SANDBOX` that fr.py:48 reads (plugin.json omits it too; defensible, but the three env lists are hand-synced). |
| glama.json | 5 | 5 | 5 | 5 | 5 | 5 | Nothing to change. |
| .claude-plugin/marketplace.json | 5 | 5 | 5 | 5 | 5 | 5 | Generated by scripts/plugin_bundle.py; guarded by tests/test_plugin_bundle.py. |
| plugin/.claude-plugin/plugin.json | 5 | 5 | 5 | 4 | 5 | 5 | Same generator and guard. `userConfig` matches server.json env vars. |
| plugin/.mcp.json | 5 | 5 | 5 | 4 | 5 | 5 | Pinned `fontes-mcp==0.1.1` equals pyproject version; guarded. |
| .github/workflows/health.yml | 3 | 4 | 4 | 4 | 4 | 3 | Header (1-8) is 8 comment lines; lines 7-8 ("Pages needs a public repo ... until then the page lives in the repo only") are likely stale for a repo named fontes-public and pyproject.toml:35 already links the Pages status URL. Verify and delete. |
| .github/workflows/publish.yml | 5 | 5 | 5 | 5 | 5 | 5 | Tag-vs-version gate, offline tests, wheel smoke test. Nothing to change. |
| .github/workflows/windows.yml | 2 | 5 | 4 | 4 | 4 | 3 | Line 3 points to docs/RELEASING.md, which does not exist (docs/ has CODE_SIGNING.md; only this file references RELEASING). Lines 24-25 narrate history ("caught a 0.1.0 bug"). Repoint to CODE_SIGNING.md or whichever doc is meant; trim comment to "Windows has no system tz database; tzdata is required". |
| .github/ISSUE_TEMPLATE/bug.yml | 5 | 5 | 5 | 4 | 5 | 5 | Install options match installer/ (macos, windows, mcpb exist). |
| .github/ISSUE_TEMPLATE/config.yml | 5 | 5 | 5 | 5 | 5 | 5 | Linked docs exist (SECURITY.md, docs/FAQ.md). |
| .github/ISSUE_TEMPLATE/jurisdiction.yml | 5 | 5 | 5 | 5 | 5 | 5 | docs/COVERAGE.md exists. |
| .github/ISSUE_TEMPLATE/source.yml | 5 | 5 | 5 | 5 | 5 | 5 | Nothing to change. |

### Adapters (src/world_legal_mcp/jurisdictions/)

| module | T | C | E | F | M | S | biggest concrete issue / cheapest fix |
|---|---|---|---|---|---|---|---|
| jurisdictions/__init__.py | 5 | 5 | 5 | 5 | 5 | 5 | none |
| jurisdictions/ad.py | 3 | 3 | 3 | 3 | 2 | 4 | dead `pre` in `_sections` (ad.py:618, 629): delete. Constitution PDF repair (ad.py:462-548, `!= 107` at :546) and hardcoded date at :351 belong in data/own module. |
| jurisdictions/af.py | 3 | 3 | 3 | 3 | 2 | 4 | `_download` (af.py:185-204) reimplements request logic via private `_http._throttle`/`_http.stats` (only users in repo): add an `_http` download helper. Threshold 1410 duplicated (af.py:140, 163); `endswith("fail for this Gazette")` at :166. |
| jurisdictions/afchpr.py | 3 | 3 | 3 | 3 | 3 | 4 | `_row()` has a pointless `for ... break` (afchpr.py:260-265); files stored twice (afchpr.py:213-215); `pend_dates` hack in search_caselaw (:334-411); two near-identical TTL caches. |
| jurisdictions/al.py | 3 | 2 | 3 | 3 | 2 | 3 | ~110 lines hand-rolled docx/doc/OLE parsing (al.py:83-196) in the adapter (bh.py has a second docx parser); Word-or-PDF fallback triplicated (al.py:306, 649, 686); `_check_filters` (al.py:237) duplicates server.py:94; unreachable archive_year check (al.py:595); base-law warning repeated 5x; `_snippet` hand-unescapes (al.py:392) instead of `html.unescape`. |
| jurisdictions/am.py | 3 | 3 | 3 | 2 | 3 | 3 | Constitution special-cased by id in code (`_OLD_CONSTITUTIONS`/`_NEW_CONSTITUTION` am.py:303-309, 286, 429-459); constitution note repeated 3x (am.py:434, 443); constants after the functions using them. |
| jurisdictions/ar.py | 3 | 3 | 2 | 3 | 3 | 3 | `search_legislation` (ar.py:368-449) ~80 lines with nested run/tier/amends, `typ in ("ley","any")` twice (:419, :424), `re.split(r"\W+", _fold(q))` 3x (:421, 429, 442); history narration "dropped on 2026-11-05" (ar.py:4, 10); `datetime.date.today()` vs `_http.today()`. |
| jurisdictions/at.py | 3 | 3 | 3 | 3 | 3 | 4 | Local `_clean`/`_iso` duplicate `_http.clean`/`_http.iso_date` (at.py:85, 95); stale "candidates for promotion" comment (at.py:74); `_resolve_ecli` prefix tuple duplicates `_PREFIX`/`_COURTS` (at.py:223); unbounded `_toc_cache` bypasses `lru_put`. |
| jurisdictions/au.py | 4 | 4 | 4 | 4 | 4 | 5 | 60-line `_Doc.__init__` (au.py:210-270); `_COLLECTIONS` duplicated in legislation_filters; import style differs (`from .._http import clean, get`). |
| jurisdictions/az.py | 4 | 3 | 4 | 4 | 4 | 4 | `_COURTS` values duplicated in `_TYPES` (az.py:39-43); `re.sub(r"\*{4}","",p)` twice (az.py:139-140); meta dict building duplicated (az.py:293, 339); charset sniffing (az.py:129-133) duplicates `ba._decode`; `_as_of` defined after class (az.py:348). |
| jurisdictions/ba.py | 3 | 3 | 3 | 3 | 2 | 3 | Three unrelated sources (Constitutional Court, FBiH registry, parlament.ba) in one 792-line file (section split at ba.py:388+); history narration "added 2026-11-10" (ba.py:41); `_registries` mixed str/int keys (ba.py:117, 601, 620); `_law` 55-line 3-branch (ba.py:709-764); `USTA V` hack (ba.py:330); `_us_json` raise without `from None` (ba.py:181). |
| jurisdictions/bb.py | 3 | 3 | 3 | 2 | 3 | 3 | CCJ logic (`ccj_appeals`, `_pdf_origin`, `_CCJ_COUNTRIES`, bb.py:168-245) is imported by bz.py:48 and gy.py:38/309 and reaches into private `_ccj._rows`/`_ccj._key` (bb.py:217, 222): move to ccj.py. OCR section-chain heuristics with magic thresholds (bb.py:303-388); date validation duplicated (bb.py:491, 511); inline `from pypdf import` (bb.py:192); `COURTS` duplicates and quote variants. |
| jurisdictions/bd.py | 3 | 3 | 2 | 2 | 2 | 3 | Bijoy-to-Unicode tables+logic (bd.py:66-98) inside adapter; `search_legislation` (bd.py:406-474) ~70 lines with lambda `squash` and duplicated cache-fetch (:431 vs :449); `not seen.add(h.id)` trick (bd.py:605); pointless `for el in pre[:1]` (bd.py:540); `_EN_BN` 2 entries / `_SUPERSEDED` 1 id hardcoded (bd.py:332-340, used :419, :465); `as_of=_http.today()` fake version date (bd.py:552). |
| jurisdictions/bg.py | 3 | 3 | 3 | 3 | 3 | 4 | `try r.json() except ValueError` repeated 5x (bg.py:148, 164, 179, 197, 446); no-op comprehension `words = [w for w in q.casefold()...split()]` (bg.py:427); `q in ("*",)` (bg.py:417); stray `_SCAN_MAX` (bg.py:76); `_clean = _http.clean` alias (bg.py:71); `search_caselaw` has no defaults (bg.py:315) unlike siblings. |
| jurisdictions/bh.py | 3 | 3 | 3 | 3 | 3 | 4 | `-> "httpx.Response":  # noqa: F821` lint hack, no import (bh.py:195); duplicate `_AR_MONTHS` key (bh.py:51); `_TYPES` values never used, only keys (bh.py:453-456); second docx parser (bh.py:134-192); `seen[_key(val)]` vs `_key(label)` inconsistency (bh.py:384-386); title regex duplicated (bh.py:505, 525). |
| jurisdictions/bj.py | 3 | 3 | 3 | 3 | 3 | 3 | `loi-2018-16` special case in code (bj.py:249-251); dead `arrete` alternative in `_LAW_ID` (bj.py:76, admitted in gaps bj.py:342); paging-window loop duplicated (`_cc_window` bj.py:407-431 vs bj.py:466-477) and clamp repeated by hand instead of `_page_window` (bj.py:378, 398); inline `import unicodedata` (bj.py:88); `search_caselaw` no defaults. |
| jurisdictions/bo.py | 3 | 2 | 3 | 3 | 2 | 3 | Three sources in one 820-line file (Tribunal Agroambiental, Cámara WP REST, LexiVox); label matching duplicated across LexiVox/Chamber branches (bo.py:783 vs 796) and `_Scan` fallback recursion 3x (bo.py:773, 793, 815); `m = [None, str(filters["number"])]` fakes a regex match (bo.py:737); `_scan_lx` only re-raises (bo.py:755-762); `_ART`/`_HEAD`/`_Scan` defined after use (bo.py:329 vs 318; 561 vs 406); `ley n` regex duplicated (bo.py:716, 735). |
| jurisdictions/br.py | 3 | 3 | 3 | 3 | 3 | 3 | `_parse` and `_parse_flat` duplicate the title/alternateName block and the return dict (br.py:315-321 vs 379-386) and `sameAs` DetalhaSigen regex (br.py:269, 624); `_parse_flat` is a dense 55-line state machine (br.py:330-386); `datetime.date.today()` vs `_http.today()` (br.py:555); `int(limit)`/`max(1,..)` re-clamp what server guarantees (br.py:498, 565); 3 hand-written `r.json()` try/except (br.py:152, 571, 611) without `from None`; docstring "verified 2026-11-05 from a UK IP" is history (br.py:4); `_SKIP` single-member set (br.py:71). |
| jurisdictions/bs.py | 3 | 2 | 3 | 3 | 3 | 4 | bs.py:383-454 Revised-Edition section splitter duplicates bz.py:271-366, and bs.py:468 `_norm_prov` duplicates bz.py:369; PDF fetch at bs.py:96-112 with its own `MAX_PDF` (:59). Fix: share one Bahamas/Belize splitter and `_http.pdf_get(url, max_bytes)`. |
| jurisdictions/bz.py | 3 | 2 | 3 | 3 | 3 | 4 | bz.py:271-366 splitter is the twin of bs.py:383-454; bz.py:273 docstring says "after bs.py/tt.py" (cross-reference instead of sharing); PDF fetch bz.py:404-419 + `MAX_PDF` :58. |
| jurisdictions/bt.py | 4 | 3 | 4 | 3 | 4 | 4 | Small file; same per-adapter label normaliser / fetch boilerplate as the family. Cheapest fix: use shared helpers. (Detail not re-checked after compaction.) |
| jurisdictions/ca.py | 3 | 3 | 3 | 3 | 2 | 4 | ca.py (785 lines) mixes SCC scraping, Justice Laws XML and a Constitution HTML parser (~438-596). ca.py:305 local `text()` is a near-twin of `_http.text` (_http.py:187; ca version lacks the None-safe-vs-localname behaviour, so check whether it can go); ca.py:279 `"streaming"` special case. Fix: split the Constitution parser out. |
| jurisdictions/ccj.py | 4 | 3 | 4 | 3 | 4 | 4 | ccj.py:282-288 fetches a PDF with no size cap, unlike every sibling (bs, bz, ci, cm, cv). Fix: shared capped PDF helper. |
| jurisdictions/ch.py | 3 | 3 | 3 | 3 | 3 | 4 | 620 lines, one class with several sources; same helper duplication. (Detail not re-checked after compaction.) |
| jurisdictions/ci.py | 3 | 2 | 3 | 2 | 3 | 4 | ci.py:127-145 + :71 repeat the PDF fetch/`MAX_PDF`; ci.py:92 `_fold` and :249 `_norm_prov` are per-adapter copies; ci.py:89 `_LABOUR` keyword list and the widening hack at ci.py:351-357 are hardcoded heuristics in code. |
| jurisdictions/cl.py | 4 | 3 | 3 | 3 | 3 | 4 | cl.py `search_legislation` (~60 lines) mixes search, `_amends`/`_AMENDING_NOTE` heuristics (:88-94, :308) and base-statute insertion (:393-409); the title-cleaning code is written twice (cl.py:379-392 and :403-407); cl.py:413-417 note expression `_AMENDING_NOTE * (sum(...) >= len(hits) > 0)` is hard to read; cl.py:362 `int(limit)` is not clamped; cl.py:51 `_later` cache sits among the constants, apart from `_cache` (:58). |
| jurisdictions/cm.py | 3 | 2 | 3 | 3 | 3 | 4 | Two unrelated sources in one file. cm.py:40 fourth copy of `MAX_PDF`; cm.py:239-253 `_pdf_text` is another HEAD-check + pdf_text; cm.py:67 `text_date` docstring itself says it "could be shared"; cm.py:498/:505 very long lines with `_AS_SIGNED{await _amenders(law)}` duplicated in both branches. |
| jurisdictions/cn.py | 4 | 4 | 4 | 4 | 4 | 3 | cn.py:48-54 retry-once comment narrates a dated health run ("two health runs 2026-11-10") = history narration; cn.py:44 module-level `asyncio.Lock` created at import. Fix: shared retry helper, drop the dated comment. |
| jurisdictions/co.py | 3 | 3 | 3 | 3 | 2 | 3 | Three sources, two jobs in 510 lines. co.py:120-121 retry on 502/503/504 with a dated "health run 2026-11-10" comment; co.py:147 `_ART` very dense regex; co.py:224 `_is_heading` 80%-uppercase heuristic; co.py:363-406 unconditional second `_soql` count query. |
| jurisdictions/cr.py | 3 | 3 | 3 | 2 | 4 | 3 | cr.py:191-195 `BASE_CODES` is data in code, and the same codes are listed again in prose at cr.py:318/:324-329; cr.py:61-67 `_id_note` uses `BASE_CODES` before it is defined (:192); cr.py:80 `_roman` knows only I,V,X,L,C; cr.py:269-329 `search_legislation` is long. |
| jurisdictions/cu.py | 3 | 3 | 2 | 3 | 3 | 3 | cu.py:172-248 `_parse` (~80 lines) does sumario titles, norms, articles, TOC and bodies; cu.py:501 `_gsearch` (~60) mixes scraping, paging and status fixing; cu.py:66 `MAX_BYTES` (different name from the family's `MAX_PDF`); cu.py:94-103 own `_MONTHS`/`_fold`; cu.py:266-274 `_gget` hand-rolled retry; ~40-line docstring with dated verification history. |
| jurisdictions/cv.py | 3 | 2 | 3 | 2 | 2 | 3 | Four sources in 731 lines. cv.py:655 dead branch: `for sec in ([section] if section else list(STJ_SECTIONS))` sits inside `if section:` (:654), so the `else` can never run; cv.py:72/:154-174 own PDF fetch + `MAX_PDF`; cv.py:99 `_fold` copy; cv.py:109-116 private TTL cache (cn and dz have their own too); cv.py:515 `SCANNED_LAWS` hardcoded ids; cv.py:628 and :688 repeat `max(1, min(int(limit), 50))`. |
| jurisdictions/cz.py | 3 | 3 | 3 | 2 | 2 | 4 | cz.py:46-100 ~90-entry `_COURTS` table in code (data file); cz.py:426-456 `_nss_form` parses a JS literal by brace counting and caches in a module global (:423); cz.py:116-137 `_json` retry loop; `search_legislation` returns no note unlike siblings. 827 lines, 4 sources. |
| jurisdictions/de.py | 3 | 3 | 3 | 3 | 3 | 4 | de.py:326-353 block tuples have two shapes (5 vs 6 elements: `("h", level, "", heading, body)` vs `("p", 0, label, enbez, titel, body)`), fragile; de.py:251-253 no-op `x.tag = "div" if x.tag == "Content" else x.tag`; de.py:55-56 `_NON_BFH_RE` hardcoded topic list; de.py:449 `search_caselaw(self, query, *, limit, page, filters)` has no defaults unlike siblings (difc, ec, echr, do_ have them). |
| jurisdictions/difc.py | 4 | 4 | 4 | 4 | 5 | 4 | difc.py:133-134 comments restate the Source field values; difc.py:204-209 `_resolve_citation` runs a full `search_caselaw` and falls through to NotFound (fine). Tight file; only nit is the repeated "no 429 seen in ~N requests" rate_limit boilerplate (also in dk, do_, dz, ec, echr). |
| jurisdictions/dk.py | 4 | 4 | 3 | 4 | 4 | 4 | dk.py:256 `bill` recomputes `_http.clean(d.get("documentType")).lower()` instead of reusing `dtype` (:255); dk.py:265-269 `note` is assigned then overwritten in the `"h" not in params` branch, so the first branch is the only place that uses the initial value - invert for clarity; dk.py:370-376 etc fine. `_blocks_xml` returns anonymous 4-tuples (dk.py:128) - a NamedTuple would read better. |
| jurisdictions/do_.py | 4 | 4 | 3 | 3 | 4 | 4 | do_.py:70-90 three near-identical date parsers (`_word_date`, `_running_date`, `_short_date`) over `_MONTHS`/`_MON3`; do_.py:93 `_fold` copy (ci, cu, cv, dz also have one - should be `_http.fold`); do_.py:234-244 note is a very long string that repeats itself ("SUBJECT SEARCH NOT SUPPORTED" + "a zero here does not mean none exist" + "Open line" explanation). |
| jurisdictions/dz.py | 3 | 3 | 3 | 2 | 2 | 3 | dz.py (797 lines) holds two sources and three jobs (JO PDF text extraction with column layout, Constitution amendment replay, WordPress case law). dz.py:58-60 `_CC_CATS` hardcoded id list; dz.py:62 `_MONTHS` + dz.py:502 `_MONTH_NAMES` are two month tables in one file (accented and unaccented); dz.py:296/:470 own TTL caches; dz.py:640-651 `gaps` entries are 400-char paragraphs with dated findings (2026-11-10, "1,794 date from before 2002") that will go stale; dz.py:663 `search_caselaw(self, query, *, limit, page, filters)` has no defaults, and `filters.get` would fail if filters is None. |
| jurisdictions/ec.py | 4 | 4 | 4 | 4 | 5 | 4 | ec.py:86 `raise SourceError(...)` inside `except ValueError` lacks `from None` (echr.py:80 and dk.py:245 have it); ec.py:191-193 limit check runs `int(limit or 10)` twice; ec.py:57-62 `_CRITERIA` is data in code but justified (wire format). Clean, compact. |
| jurisdictions/echr.py | 4 | 4 | 3 | 4 | 4 | 4 | echr.py:163-253 `search_caselaw` is ~90 lines building a query string through a long chain of ifs; the case-name phrase retry (:217-227) duplicates the `_query` call; echr.py:234-237 article post-filter repeats `.strip().lower()` 4x. Fix: split `_build_query(filters)`. |
| jurisdictions/ecowas.py | 4 | 3 | 3 | 3 | 3 | 4 | Decision-list scraper and Law Report PDF parser share one 640-line file. `words` tokenisation is duplicated at :474 and :534. Redundant f-string at :214 (`row["nature"] and f"{row['nature']}"`). Hardcoded kind dict at :539. Fix: dedupe the two clamps/tokenisers, drop the f-string. |
| jurisdictions/ee.py | 4 | 3 | 3 | 4 | 4 | 3 | `search_legislation` (:356-445) is long and its note repeats the koostöölepingu/tööleping compound sentence twice. A "(Fontes note: ...)" string is spliced into Provision text at :466 although `Provision.note` exists. Gaps :346-348 say "not researched yet" / "source works but not built". Fix: use `note`, dedupe the sentence. |
| jurisdictions/efta.py | 4 | 3 | 4 | 4 | 4 | 4 | `_resolve` (:246) and `_decision_doc` (:278) rebuild the same downloads dict. Limit clamp duplicated. Gaps :152-153 are weak. Fix: one helper. |
| jurisdictions/eg.py | 3 | 3 | 3 | 4 | 4 | 4 | `_NO_MATCH` filter applied twice (:213, :219). `search_caselaw` (:175-248) is long with a patchwork note. Gap :168 "not researched yet". Fix: filter once, split note. |
| jurisdictions/es.py | 3 | 3 | 3 | 4 | 3 | 4 | BOE and the TC (ASP.NET) are unrelated sources in one 660-line file. `_hj_search` annotated `-> list[str]` at :336 but returns str (:357, :368). `_today()` at :89 duplicates `_http.today`. `_NOTICE`/`_NOTICE_OUTDATED` (:62-67) near-duplicates. Fix: fix the annotation, use `_http.today`, split TC out. |
| jurisdictions/et.py | 4 | 4 | 3 | 3 | 4 | 4 | `NOT_HELD` (:74-77) hardcodes a "searched 2026-11-12" claim. `eth_num` public among private helpers. Hardcoded `_JUNK`/OCR heuristics (:68, :70). Gap :262 "not researched yet". Fix: make `eth_num` private, move the date claim into gaps. |
| jurisdictions/eu.py | 3 | 3 | 3 | 3 | 3 | 4 | Stale comment :89 "candidates for promotion to a shared module". `_clean` (:105) duplicates `_http.clean`. `_STEMS`/`_STAFF_WORDS`/`_competition_noise` hack (:109-116) is hardcoded. `datetime.date.today().strftime` at :618 duplicates `_http.today`. Error at :554 omits "treaty". Fix: delete `_clean`, use shared helpers. |
| jurisdictions/fi.py | 3 | 3 | 3 | 3 | 3 | 4 | AKN legislation and RSC case-law parser share one 797-line file. year/since validation duplicated at :601-606. Redundant `want = None` :611. Odd single-element tuple checks :231-233. `_laws` is a class-level mutable cache. `_api_page` (:148) is live (used :708). Gaps :572, :579 "not researched yet". Fix: split case law, dedupe validation. |
| jurisdictions/fr.py | 3 | 3 | 3 | 4 | 3 | 3 | Docstring (:1-32) narrates history ("Written from the public docs only, before any key existed (2026-11-10)", "Unverified until real keys exist"). Date/sort/operator checks duplicated at :172-187 and :398-415. `_lf_body` (:376-383) checks `limit > 100` then also clamps. `search_caselaw` (:528-576) mixes two sources plus a loose-match heuristic (:543-555). `_fold` (:214) is a copy. Fix: shared validators, drop history text. |
| jurisdictions/gb.py | 3 | 3 | 3 | 3 | 3 | 3 | Docstring "Ported from uk-legal-mcp" is history. `_COURT_LABELS` (:223-263) is a large hardcoded map with an inconsistent label at :252. `_COMMENTARY_LABEL`/`_KEEP_INHERITED` (:596-601) are parked mid-file. `_search_caselaw` (:94-182) has a 3-way fallback and `+=` note. `_search_legislation` recurses (:483) only to get a total. One-line module wrappers `_get_judgment`/`_get_toc`/`_get_provision`/`_get_text` delegate from class methods. `_title_rank` duplicates ge. Note :758 says "requires ALL words" though code falls back to phrase variants (stale). Gap :765 "not researched yet". Fix: remove wrappers, correct note. |
| jurisdictions/ge.py | 3 | 3 | 3 | 3 | 3 | 4 | `_UNSUP` (:38) is dead (only definition in ge; ee has its own). `_title_rank` (:270) duplicates gb. `_check_iso` (:294) is another ISO-date copy. `_ka_date` (:254-267) tests `m.re.pattern.startswith("(\\d{4})")` (hack). Overlong meta line :516. `search_caselaw` (:366-411) and `get_decision` (:413-448) long. Regex over raw HTML (:114-118, :211-219). Gap :354 "not researched yet". Fix: delete `_UNSUP`, share helpers. |
| jurisdictions/gr.py | 4 | 3 | 3 | 3 | 4 | 4 | One-off "μισθωση" special case at :455-458 inside generic search logic. `_fold` (:77) copy. `_ap_get` picks post vs get by `"data" in kw` (:E). `search_caselaw` (:413-460) long. Gap :402 "not researched yet". Fix: drop or table the special case; two explicit calls. |
| jurisdictions/gt.py | 4 | 4 | 4 | 3 | 4 | 3 | Docstring (:4-21) is mostly dated research narration ("Retried 2026-11-10 ...") and repeats the three gaps entries. `_plain` (:57) is a fold copy. `_fix` (:89-94) hardcoded OCR repair list. Fix: cut the docstring to how the source works; leave facts in gaps. |
| jurisdictions/gy.py | 3 | 3 | 3 | 3 | 3 | 3 | `_split` (:99-188) is a 90-line PDF-arrangement function "adapted from bs.py / tt.py" (duplicated logic). Reaches into private names of other adapters (`_ccj._key/_rows/_cite`, `_bb._listed_origin/_origin/_pdf_origin`, :303-312). Magic `27` (:320) and `"2022-12-31"` twice (:358, :363). Signature defaults `limit=10, page=1, filters=None` differ from siblings. Notes :295-300, :337-341 overlong with ragged wraps. Docstring research narration :20-25. Fix: extract shared PDF arranger, make the cross-adapter helpers public. |
| jurisdictions/hk.py | 4 | 3 | 3 | 4 | 3 | 4 | Remote ZIP-over-Range code (:59-108) is a general utility inside the adapter (its comment calls it shareable; `_central_directory`/`_zip_member` have no callers outside hk.py). `_size` unused tuple element (:180, :189). `(c.get("Version") or [{}])[0]` repeated 4x (:155, :176, :477, :494). Hand-rolled TTL cache with `time.time()` (:116). `search_legislation` (:448-503) long with inline maps. Fix: move ZIP reader to `_http`/own module, add a `_latest_version()` helper. |
| jurisdictions/hn.py | 3 | 3 | 3 | 3 | 3 | 3 | Docstring (:4-33) is a dated research log ("Retried 2026-11-10 ...") duplicated by gaps. Two sources (TSC library and ENAG gazette: `_enag_month`, `_enag_load`, `_search_gaceta`) in one file. `_cache` shared by three key kinds (month/id/law). `_enag_month` picks `[k ... if k!="setiembre"][0]` (:217). Hardcoded suffix list `bis/ter/quater/a/b/c` (:153) and match map (:371). `search_legislation` (:363-433) long; note :424-428 very long. `_fold` copy (:68). Fix: trim docstring, split ENAG, separate caches. |
| jurisdictions/hr.py | 4 | 3 | 3 | 4 | 4 | 4 | `search_caselaw` filters titles to "Ustavnog suda" at :309, then recomputes `is_usrh = "Ustavnog suda" in x["title"]` (:312) and branches on it at :314-315, so the false branch is dead. The amending-act regex is duplicated at :244 and :423. `_articles` has unused loop vars `k`, `label` (:383, :389) and a two-pass start computation. `_status` is a long message builder with an inline Constitution special case (:419-422). `_is_title`/`_is_heading` hardcoded thresholds 0.8/160/200 (:106, :111). Docstring "verified 2026-11-05 from a UK IP" is dated. Fix: remove `is_usrh`, hoist the amending regex to a constant. |
| jurisdictions/ht.py | 4 | 4 | 4 | 3 | 4 | 3 | Docstring (:1-31) is largely dated research history (counts "In 2026-11 it held 22 PDFs", "Constitution (added 2026-11-10)", "Not used" list) that gaps and `research/ht.md` already hold. `_fold` copy (:66). Public `fr_date` and `norm_provision` have no callers outside ht.py (grep). `_library` paging loop hardcodes `n <= 5` (:100). "~17 laws" figure repeated in warning :245, notes :263, gaps :267, note :285 (will rot). Fix: trim docstring to mechanics, state the count once, make helpers private. |
| jurisdictions/hu.py | 4 | 4 | 4 | 3 | 5 | 4 | `search_caselaw` doesn't clamp `limit`/`page` (:160) unlike siblings. Magic `len(form) == 3` (:181) is a fragile "no filters" test. `_KOLLEGIUM` hardcoded (:29). One blank line before `_CASE_NO` (:92) breaks the file's spacing. Gaps :142-143: "works but not built yet", "not researched yet". Fix: track a `has_criteria` flag, clamp, relabel gaps. |
| jurisdictions/icj.py | 3 | 3 | 3 | 3 | 3 | 4 | 597 lines mixing case law (HTML search/case records) and legislation (Statute/Rules scraper, `_LAWS`, `_law`). `_LAWS` third tuple element (keyword string) is never read (`title, url, _ = _LAWS[lid]` :268; `_` at `search_legislation`). `search_caselaw` (:~370-450) is ~100 lines with a nested-ternary note `how=(...)` and `ranked = how_order = False`. `_STOP`/`_KINDS`/`_ORDER` hardcoded tables (`_ORDER` duplicates `_KINDS` values). `_law_id` has a redundant `"/statute"` test (subsumed by "statute"). `_PDF_NOTE` wedged between functions. Gap "PCIJ ... not researched yet". Fix: drop the unused tuple member, split law pages into their own module, flatten the note. |
| jurisdictions/icsid.py | 4 | 4 | 4 | 3 | 4 | 4 | `_STATE_STYLE` (:61-67) hardcoded alias table (partial: no Germany, Spain, Venezuela etc.). `_fold` (:54) copy. Hand-rolled `time.monotonic` TTL cache (:91-102). `search_caselaw` (:253-320) mixes validation, filtering and note building. Clamp duplicated. Fix: use shared fold, split filter predicate. |
| jurisdictions/id.py | 4 | 3 | 3 | 3 | 3 | 4 | id.py:533-579 get_legislation_provision mixes label parsing, status lookup and banner; status fetch swallows SourceError with bare `pass` (:563). JDIH search, PDF repair (_mend/_paragraphs/_structure) and UUD special case share one 620-line file; split the PDF/UUD part. Hardcoded OCR regexes/_VARIANTS :65-87; `_structure` third return discarded in _uud (:469). |
| jurisdictions/ie.py | 4 | 3 | 3 | 3 | 2 | 4 | ie.py:325 _load_si and :353 _load_pre1922 duplicate fetch/404/layout-check; hand-built HTTP SourceErrors although _http.error exists; loaders, XML normaliser, Constitution scraper (:391 regex slicing HTML) and adapter in one 663-line file. _Doc (:217) plain class; note duplicated into metadata (:659) and text (:662). Fix: one shared loader, move Constitution scraper out. |
| jurisdictions/il.py | 3 | 3 | 3 | 3 | 2 | 4 | il.py:147-256 PDF cmap/RTL repair is a separate subsystem in the adapter; `except Exception: pass` at :167 and :181 hides failures; _gazette_doc returns untyped 5-tuple (:259) and _official mutates doc[4] (:556); `ch.tag in ("p",)` (:347). Fix: extract gazette-PDF module, return a small dataclass. |
| jurisdictions/in_.py | 4 | 3 | 3 | 3 | 3 | 4 | in_.py:237 `if m := _SC_PATH.match(i): return i` binds m unused (dead binding, also :239); search_caselaw :337-405 is ~70 lines mixing year parsing, since/after heuristics and scoring; _SC_STOP hardcoded (:171). Two unrelated sources (India Code, SC mirror) in one file. |
| jurisdictions/iq.py | 4 | 3 | 3 | 3 | 4 | 4 | iq.py:272-361 search_legislation ~90 lines with duplicated year validation; import-time mutation of ordinal dicts :75-77; redundant `as_of=""` :370, :390; pointless optional prefix in _check_id regex :132. Fix: split validation from query, drop the no-op args. |
| jurisdictions/is_.py | 4 | 3 | 3 | 3 | 4 | 4 | is_.py:253-334 search_caselaw ~80 lines of merge/paging; odd `items.extend(sub_items[lo - first * 10:] if not both else sub_items)` :310; _stem heuristic :112 and _COURTS :49 hardcoded. Fix: extract paging merge helper. |
| jurisdictions/it.py | 4 | 3 | 3 | 3 | 3 | 4 | it.py:51 _ABBREV hardcoded and reused as validity list :373; search_legislation filter-validation chain :325-381; get_legislation_provision :388 dense; _is_art/_trim as staticmethods rather than module helpers. Fix: derive validity from one table, hoist helpers. |
| jurisdictions/itlos.py | 4 | 4 | 4 | 3 | 4 | 4 | itlos.py:203-218 _pick_order uses prose regexes; _TYPES (:47) and stop-word list (:279) hardcoded; odd note indentation :298-299; `[{}]` fallback plus `if main:` awkward :335-337. Small items only. |
| jurisdictions/jm.py | 4 | 3 | 3 | 3 | 3 | 4 | jm.py:341-416 search_caselaw ~75 lines of three-source paging arithmetic; module-level mutable caches _ca_cache/_ca_years/_sc_years (:61-64); _ca_list :171-195 nested cache/year-menu logic; hardcoded fallback '1962' :142; hand-built SourceErrors :185, :210, :259. Fix: one source-paging helper, use _http.error. |
| jurisdictions/jo.py | 4 | 4 | 3 | 3 | 4 | 3 | jo.py:22-26 and :243-245 narrate the 2026-11-10 outage (history, stated twice); _pager_links magic offsets `+ 4000`, `+ 200` (:138-139); _form regexes fragile (:113-125); positional `Results(hits, None, ...)` :293-295. Fix: delete the outage narration, name the offsets. |
| jurisdictions/jp.py | 4 | 3 | 3 | 3 | 4 | 4 | jp.py:80 _child is a trivial el.find wrapper (5 uses); _blocks :84-138 long if-chain with Paragraph tag tuples duplicated :114-116 / :121-122; _status (:275) and _hit (:456) both do the _STATUS lookup; hand-built SourceError :296 instead of _http.error; stray quote in _arabic docstring :177. |
| jurisdictions/kg.py | 4 | 4 | 3 | 3 | 4 | 4 | kg.py:36, :43, :44, :89 category ids repeated in four tables; _stem :69-85 hardcoded Russian-morphology heuristic; `_type(cats)` computed twice at :216; terms_url="" :125. Fix: one category table, compute once. |
| jurisdictions/kh.py | 3 | 3 | 3 | 3 | 4 | 4 | kh.py:158 _parse returns (marks, lines) but all three callers discard the second (`marks, _ =` at :294, :306, :318): return only marks. _list_cache dict holds one "all" entry (:61, :91, :120); `f = filters or {}` after `(filters or {})` already used (:252, :258); _meta duplicates item dict shape :124-130; Khmer regex/date heuristics hardcoded. Gaps repeat the docstring. |
| jurisdictions/la.py | 4 | 4 | 4 | 3 | 4 | 4 | la.py:84-89 bare `except Exception` retry with test-run history in the comment (:84-85); :119-120 comment narrates a past complaint; _ENGLISH :56-68 has redundant labour/labor entries; odd line breaks `Results(items=[], total=total,\n note=...)` :179-180, :188-189; scans-only fact stated in docstring, warning, notes and gaps. Small items. |
| jurisdictions/lb.py | 4 | 3 | 3 | 3 | 3 | 4 | lb.py:279-369 search_caselaw ~90 lines with two paging modes and magic numbers `range(1, 41)` :327, 30 :386; 5-tuples (part, url, ch, label, text) passed around :207, :470; "1926-05-23" hardcoded twice :428, :438; `legislation_filters = {}` :257 equals the base default (base.py:88), delete. |
| jurisdictions/li.py | 3 | 3 | 3 | 3 | 3 | 4 | li.py:140-220 _parse_text 80-line state machine over an untyped dict (:135); "2020-2025" hardcoded in filters/notes/comments (:316, :328, :362) while years are read dynamically (:259), stale once 2026 exists; _ogh_index module-global list with no TTL (:223, :268); hand-built HTTP SourceErrors :117, :229, :379, :414; mis-indented gaps :331, :335. Lilex and OGH in one file. |
| jurisdictions/lu.py | 3 | 3 | 3 | 3 | 2 | 4 | lu.py: legislation (SPARQL/Akoma Ntoso) and Cour de cassation ZIP-by-Range case law are separate subsystems in one 726-line file; hand-rolled ZIP central-directory parser with magic offsets :359-391; search_caselaw :529-615 ~85 lines with nested fold_map/lambda :587-594; _TMAX mid-file :93; _res_cache["res"] with hardcoded 1800 TTL :335; docstring :25 dated "added 2026-11" history; hand-built "returned HTTP" errors :100, :339, :414. Fix: split caselaw ZIP into its own module. |
| jurisdictions/lv.py | 4 | 3 | 3 | 3 | 4 | 4 | lv.py:132-155 local _pdf_text duplicates _http.pdf_text (needs layout mode; broad `except Exception` :137, in-function import :133); UUID court table :42-67 plus duplicated alias dict :68-71; `len(body) == 4` magic :248; cryptic one-use `cc` :265; hand-built SourceErrors :122-128, :163. |
| jurisdictions/ly.py | 4 | 3 | 3 | 3 | 2 | 3 | ly.py: MoJ legislation (WordPress + PDF, :55-316) and Supreme Court RSC scraper (:319-482) are two independent subsystems in a 708-line file; docstring :1-54 is mostly source-quirk detail (fine) but dates/history ("verified 2026-11-10") repeat in gaps and notes (:534-551 gaps overlap docstring "Not used"); hand-built `Error (...)` SourceErrors :239, :278, :281, :284, :613 beside _http.error; `except Exception` retry :245; search_legislation :631-681 mixes paging, title-first ranking and hit building; hardcoded ordinal tables :95-105 and CAT_NAMES :80-88 (data, acceptable); mis-indented gaps :536, :539. Fix: split SC into own module, use _http.error everywhere. |
| jurisdictions/ma.py | 4 | 3 | 3 | 3 | 3 | 4 | ma.py:166-203 _parse is one 40-line loop with nested prev-tracking and _unglue heuristics (:148-163, magic `+ 50`, `+ 5`); search_caselaw :285-339 mixes year validation, chunked newest-first scan and item building; `_ART`/`_XREF` regexes :60-62 very long single lines; year_from/year_to validated twice (:287, :411); _law returns a 5-tuple (:450) unpacked with `_` in three callers. Fix: small dataclass for the law, shared year validator. |
| jurisdictions/mc.py | 4 | 4 | 4 | 3 | 4 | 4 | mc.py:297-348 search_caselaw: `query.strip()` repeated 6 times, `(query or "").strip()` tested three times (:300-301, :325); `must[2] =` index-based mutation :330 is fragile; _law_title (:238) and _content (:167) are trivial one-line wrappers; TYPE_LABEL/NATURES lookups chained in one expression :428. Docstring is information-dense. Small items. |
| jurisdictions/md.py | 4 | 3 | 3 | 3 | 3 | 4 | md.py:506-585 _constitution is an 80-line parser with a block list of heterogeneous tuples; `_clean = _http.clean` alias :84; dead-ish `_FUTURE` sentinel string stored in `DecisionHit.date` then patched (:99, :361, :396) instead of a separate flag; `date.today()` :395 although `_http.today` exists (:306 of _http.py); bare `except Exception` :364; helpers/constants defined after the class (:466-590) while used inside it; `nested def f` inside loop :387; hardcoded _INSTANCES option ids :67-76 and 143 article cap :475. Fix: move constitution parser to its own module/top of file, drop alias. |
| jurisdictions/me.py | 3 | 4 | 3 | 3 | 2 | 3 | OLE2/.docx parser inside an adapter (me.py:116-220); `get_decision` ~100 lines with nested cold-cache loops (402-504). Move parser to a shared helper or trim; `_this_year` trivial wrapper (81). Gaps indentation (271-279). |
| jurisdictions/mg.py | 3 | 4 | 4 | 3 | 4 | 3 | Query-triggered hardcoded dated notes for constitution/code pénal/code civil (mg.py:390-400); `import datetime` inside function (82); `legislation_filters = {}` redundant (308); `_ART` defined after use (242). |
| jurisdictions/mm.py | 3 | 3 | 3 | 3 | 4 | 3 | Broken indentation / over-long note string (mm.py:419-421); split `from ..base import` (70-71); manual `while n <= 10` (120-144); magic thresholds in `_usable` (155-163); duplicated MAX_PDF check (225, 228); hardcoded counts in notes. |
| jurisdictions/mn.py | 4 | 4 | 4 | 3 | 5 | 4 | `_CAT_NAME`/`_LEVEL_NAME` hand-kept inverses (mn.py:44-45); duplicated date-mismatch branches (274-284); `page[:i]` with possible i == -1 (285). Derive inverse from one dict. |
| jurisdictions/mt.py | 3 | 4 | 3 | 3 | 4 | 4 | Dense heuristic `_page_lines`/`_parse` with magic numbers (mt.py:106-157, 225-264); no-op `elif over: pass` (255-256); `_NOTE_META.pattern[1:]` spliced into another regex (234). Delete the no-op. |
| jurisdictions/mu.py | 3 | 3 | 3 | 3 | 2 | 3 | 919 lines, one file for 4 sources (Supreme Court library, AG SharePoint, NA table, JCPC) plus a PDF text-repair engine (_despace :410-444, _strip_running, _parse_law) with only `mu` as caller: split out the Revised Laws/Constitution part. Concrete: mu.py:823-828 runs `_despace` twice for the Constitution (once at :823 for all revised laws, again at :826) and tests `item["type"] == "Constitution"` twice (:825, :829); `_TYPES` third tuple field ("Act", :90-92) is discarded (`_` at :766) and duplicates `_TYPE_NAMES` (:98); `_ORD` contains the typo "SEVNTH" with a special case at :251; line :96 is a stray over-long line in `_TYPE_ALIASES`; `_AG_LIST`/`_cache["index"]` TTL logic hand-rolled while other adapters use lru_put. Docstring :6-45 is dense but informative; GATED text repeated in docstring :10-14, GATED :70, Source warning :481-486, notes :529-534 (same "robots Disallow: / since 2026-11-10" four times). Note: `search_legislation` :726-790 mixes local-index and live-library paths with mutated `page` (:751). |
| jurisdictions/mv.py | 4 | 3 | 3 | 3 | 4 | 4 | `_gz_id` dispatch repeated in three methods (mv.py:484, 498, 520); `_norm_id` message mentions 'gazette/7561' that `_ID` rejects (409-414); both hosts in `min_interval` (276); regex HTML splitting (`_gz_hits`). |
| jurisdictions/mz.py | 4 | 3 | 3 | 3 | 4 | 4 | Local `_pdf_text` with font-shift hack re-implements `_http.pdf_text` (mz.py:168-195); `COURT_FILTER` derivable from `COURTS` (87-89); inline English month dict despite `_http.en_date` (316-317); `search_caselaw` mixes paging/date/notes (502-540). |
| jurisdictions/ng.py | 3 | 3 | 3 | 3 | 2 | 3 | Five sources in one file (Supreme Court API, NIPC, NASS, PLAC, FAOLEX); `_pdf_text` duplicates `_http.pdf_text` which the same file uses at 378 (ng.py:188-206); 90-line `search_caselaw` (564-650); 68-line docstring with dated narration (1-68); `as_of` "2023-04-01" twice (552, 558); stale counts in notes. |
| jurisdictions/nl.py | 4 | 3 | 3 | 4 | 4 | 4 | ~120-line `_search_caselaw` with recursive retries (nl.py:201-321); `_html_to_md`/`_clean_md` duplicate `_http.html_to_md` (121-131); `_KINDS` identity dict (95); wholesale cache clear at >12 instead of `_http.lru_put` (578); no XMLSyntaxError guard at 564. |
| jurisdictions/no.py | 4 | 4 | 3 | 4 | 4 | 4 | `search_caselaw` long multi-branch (no.py:224-298); `_num_slug` defined after use (112); no-op `t not in ("*",)` (243); `_entries()` awaited twice in `_resolve` (104, 112); hand-rolled TTL cache (43, 70). |
| jurisdictions/np.py | 3 | 4 | 4 | 3 | 4 | 4 | np.py:210-289 `search_caselaw` repeats the same "Dates are Bikram Sambat... newest first... Only Supreme Court" note string in two places (:265-272, :287-289) - hoist one constant. np.py:98 `_root` is a one-line alias of lxml.html.fromstring; :309 `status_code in (200,301,302,404)` is a brittle status list. `_GENERIC` (:62) is a hardcoded stop-word list inside ranking code. |
| jurisdictions/pa.py | 3 | 3 | 3 | 3 | 4 | 4 | `(h.get("original") or {})` repeated ~10x (pa.py:366-397, 477-484); three near-identical TEXTO UNICO reorder branches (364-378); double CONTENIDO check in `_load` (186, 198); `_type` defined after use (199); `habeas` special case (495-500). |
| jurisdictions/pe.py | 3 | 3 | 3 | 3 | 3 | 3 | pe.py:513 `),        Source(` has two statements run together on one line (formatting defect); pe.py:230-235 `_turbo` fine. 816 lines mixing TC case law, El Peruano, and the Constitution glyph-decoder (:319-392); `_split_pdf` (:333) is only used for PDF-sourced norms. `search_legislation` :681-781 defines two nested async functions `run`/`run_pubs` plus three special-case branches (named law :744-756, code :771, constitution :776) - one idea per function would read better. Hardcoded prose in :765-775 notes ("Ley 27444, Ley 28611") are examples that can go stale. `_sections` unpacking `lab2` unused (:810). :806 `note=note)` odd line wrap. `_PROC_WORDS` (:83) hand list. Source `probe` comment :498-499 fine. |
| jurisdictions/ph.py | 4 | 4 | 3 | 3 | 4 | 4 | `LAW_TYPES` 6-tuple unpacked positionally (ph.py:208, 214); `_strip_tags` (143) overlaps `_http.clean`; `_MONTHS` (76) overlaps `_http.en_date`; trivial `_CASE_NO` (78); WARNING/Source string duplicated (426, 510). |
| jurisdictions/pk.py | 3 | 3 | 3 | 3 | 3 | 3 | Mixin `_PakistanCodeLegislation` (pk.py:278-443) exists only to carry a Source and legislation methods; its docstring (279-287) and module docstring (1-3) narrate TLS history and claim the class works around the TLS chain though that lives in `_http` (stale). Phrase-shortening loops duplicated (335-343, 530-545); `_shortened` (78, 547) never evicted; 100-line `search_caselaw` (494-591). |
| jurisdictions/pl.py | 4 | 4 | 3 | 4 | 4 | 4 | Two parallel result types `_Law`/`_PdfLaw` with `isinstance` branching in every legislation method (pl.py:599, 618, 644) and duplicated toc/text assembly; `_top_units`/`_depth` defined after the class that uses them (663-679); `want` part_2/part_1 re-derives `consolidated` (365); `law.warning()` called twice (634, 653); `Source` text "~10 requests" counts (423). Give `_PdfLaw` the same interface (note as property/method inconsistency: `note` is str on `_PdfLaw` at 284 but method on `_Law` at 232). |
| jurisdictions/ps.py | 4 | 4 | 3 | 4 | 5 | 4 | `_search` is ~65 lines of stacked note assembly (ps.py:189-257) with repeated diacritic-stripping regex (224, 233) and a retry path using tuple index `alt[0]/alt[3]` (203); `_collect` returns a 5-tuple (186). Name the result (small dataclass) or split note building. Long single-line `note=` f-string (255). |
| jurisdictions/pt.py | 4 | 4 | 3 | 3 | 4 | 4 | `legislation_filters = {}` redundant (pt.py:408); `search_caselaw` ~65 lines with TC and DGSI branches inline (435-498) and DGSI/TC rows parsed by regex (146-148, 205-207); hardcoded Código Penal / arrendamento urbano special cases in `_code_name_hit` (604-625); `key = _http.clean(key)` double clean (602-603); `_CODE_NAMES` dict used as a one-key holder (247, 589); own `_MONTHS` (84) and `_us_date` where `_http.iso_date` exists. |
| jurisdictions/py.py | 4 | 3 | 3 | 3 | 3 | 4 | py.py:~255 Constitution id 9580 is special-cased inside search; `except Exception: text = ""` in get_decision swallows errors. Move the id to a data table and catch the specific error. |
| jurisdictions/ro.py | 4 | 3 | 2 | 3 | 3 | 4 | ro.py:285-384 search_legislation is ~100 lines; `_clean = _http.clean` alias (58); trivial `_text` wrapper (167); `_fold` (163) duplicates the inline translate at 100; ranking regex 352 and list 341 are hardcoded. Split the search and drop the aliases. |
| jurisdictions/rs.py | 3 | 3 | 3 | 3 | 3 | 4 | rs.py:392-483 `_law` is ~90 lines with nested closures and `nonlocal`; unused `lat` title (322); unused loop vars (351); double blank line (315-316). Flatten `_law`, delete the unused bits. |
| jurisdictions/rw.py | 4 | 3 | 3 | 3 | 3 | 4 | rw.py:609 a "Note:" is embedded in `Provision.text` although `Provision.note` exists; amending-article regex duplicated (582, 598); `LAW_HINTS` (196-207) repeats "penal"/"criminal". Use the note field, hoist the regex. Gazette column-splitting PDF code (216-293) has its own concern and could move out. |
| jurisdictions/sc.py | 3 | 2 | 3 | 3 | 2 | 4 | sc.py:104-146 date regexes repeated; type map inlined at 726 and 764 instead of `_TYPE_WORD` (70); magic TTL 3600 at 554 vs `_LAWS_TTL`; "WARNING:" stuffed into a snippet (592). Three sources and two law parsers in 795 lines: split per source. |
| jurisdictions/se.py | 5 | 4 | 4 | 3 | 4 | 4 | se.py:372 HOVR aliases and `_COURTS`/`_HOVRATT` hardcoded; magic `_RD_SZ`. Small items only. |
| jurisdictions/sg.py | 5 | 4 | 4 | 4 | 5 | 5 | sg.py:211 `Results[DecisionHit]` return annotations that no other adapter uses; hardcoded `_COURTS`. Drop the annotations. |
| jurisdictions/si.py | 4 | 4 | 4 | 4 | 4 | 3 | si.py:25-29 dated outage narration ("2026-11-10 ... Code unchanged"), repeated in `gaps` 296-297; tag-strip regex repeated (126, 427); `_json` (71-89) near-duplicates sk/tj helpers. Delete the narration. |
| jurisdictions/sk.py | 4 | 3 | 3 | 3 | 3 | 4 | sk.py:319-397 search_caselaw is ~80 lines of heuristics; trivial `_label` wrapper (166); redundant `isinstance` (150); `_STRUCT.get(kind,5) if kind in _STRUCT else 4` (174) is odd (default differs by branch). Split heuristics out. |
| jurisdictions/sn.py | 3 | 3 | 3 | 2 | 2 | 3 | sn.py:86 `_PDF_ART` and 101 `_ART` are near-duplicate regexes; `_MJ_KEEP`/`_MJ_DROP` hardcoded (83-85); history narration ("added 2026-11-10") at 30, 42; "now and then hangs" comment (479); `_docs` holds an unnamed 5-tuple; `search_*` signatures lack defaults (397, 506). Four sources in one file: split per source. |
| jurisdictions/sr.py | 4 | 3 | 3 | 2 | 3 | 4 | sr.py:200-273 PDF article splitter is dense and heuristic; hardcoded Dutch ordinal regex (173); magic `>=3`, `*5000` (197); `_law` returns an untyped dict and "Let op" meta key doubles as a flag (326, 520). Use a small dataclass for the law record. |
| jurisdictions/tj.py | 4 | 3 | 3 | 3 | 2 | 4 | tj.py:292-332 `_law` three-way dict builder; 468-525 search_legislation ~55 lines; `_docs` mixes Decision objects (key `("dec", pid)`) with law dicts; magic "текст" (531, 536). Three sources in one file: split. |
| jurisdictions/tm.py | 3 | 3 | 3 | 2 | 3 | 4 | tm.py:425 `date` unpacked but unused; `_const_hit` hardcodes "2016-09-14" and "21.01.2023" (also 277); "05.11.2025" repeated (451, 475); Civil Code note hardcodes "2025-06-28" (477-481); typo `hits =[` (393); `_structure(paras)` recomputed per toc/provision call; `_docs` holds an unnamed 6-tuple. Move the dates into data, cache the structure. |
| jurisdictions/tr.py | 3 | 3 | 3 | 2 | 2 | 4 | tr.py:1-1304: six sources in one file. `_get_other` (1079-1151) and `search_legislation` (1154-1240) are ~70-90 lines each; retry-on-network-error hand-coded twice (784-785, 904-911, both with dated comments); `E. {esas}, K. {karar}` built 3 times (753-755, 805-806, 1031-1033); `_lru(_hits, did, hit, 1000)` repeated 6 times; "Anayasa"/2709 special case (1195-1204). Split per source first; extract the retry and case-string helpers. |
| jurisdictions/tt.py | 4 | 3 | 3 | 3 | 3 | 4 | tt.py:204 `_split_plain` uses `_PAGE_JUNK`/`_SEC`/`_SCHED` defined later (259-265); `_law` (639-729) ~90 lines building an untyped dict; redundant `as_of = ""` (685) and dict-copy comprehension (676); reaches into private `gb._search_caselaw`/`gb._get_judgment`; hardcoded `_OTHER_PC` (77-82) and Constitution id `u120718` (719-722). Move constants above use; stop using the private gb API. |
| jurisdictions/tw.py | 4 | 4 | 4 | 4 | 4 | 4 | tw.py:355-356 recomputes the cache key `f"{court} / {query}" if court else query` three times (also :106) - compute once. tw.py:410 `md = (f"{_AMEND_NOTE}\n\n{md}")` redundant parentheses; the A0000001 special case appears in two places (:409, :417), hardcoded pcode. tw.py:112 `{k: v for k, v in re.findall(...)}` is `dict(...)`. |
| jurisdictions/untc.py | 4 | 3 | 3 | 3 | 4 | 4 | untc.py:48 and 368 hardcoded `_ROMAN` plus `_roman()`; `_MONTHS` duplicate (51); `dict.fromkeys(x[0] for x in _SECTIONS)` repeated (462, 608); redundant try/except sets `exact=""` (541-544); redundant `art(?:icle)?\.? / art\.` alternation (471); `esc = lambda` with `# noqa` (242). Hoist the repeated expression to a constant. |
| jurisdictions/us.py | 3 | 3 | 3 | 2 | 2 | 4 | us.py:70-88 `_POPULAR`/`_POPULAR_USC` hardcoded dicts (stale-prone); `if page > 1: return Results(items=[], total=1)` repeated 5 times (626, 635, 641, 663, ...); `_is_const`/`_is_act`/else dispatch repeated in every legislation method (706-835); function-level `import io` (285, 1132), `import html as htmlmod` (1075) while top-level imports exist; pypdf guard duplicated (300, 1129); `_roman` (939) duplicates untc; magic `1 + 7 + 27` (1001); `_FIRST_PLAW` defined (1011) after use (651, 696). Five sources in one file: split. |
| jurisdictions/uy.py | 4 | 3 | 3 | 3 | 3 | 4 | uy.py:333-340 and 388-394 the heading-diff loop (same/prev) is duplicated between toc and text; `_law_id` (86-106) heavy regex normalisation; `CODES` hardcoded (49-65); `_fold` (74) and `_tags` (79) local copies; `int(limit)` repeated (320-321); `_parse` returns an untyped dict. Extract the heading-diff helper. |
| jurisdictions/uz.py | 4 | 3 | 3 | 3 | 4 | 4 | uz.py:200-280 `_doc` is an 80-line loop with a repeated "close open_label" block (240-242, 248-250, 265-267, 269-270); `_TITLE_FILLER` hardcoded (87-88, misaligned indent); `_norm_provision` builds `str.maketrans` inline (286) instead of using `_SUP` reversed; search_caselaw (367-418) has a 20-line `note` assembly. Extract `_close()` for the span bookkeeping. |
| jurisdictions/vn.py | 3 | 3 | 3 | 3 | 2 | 4 | vn.py:63, 303, 341 `_texts` is one cache shared by vbpl (key numeric id e.g. "32801") and chinhphu (numeric docid e.g. "183188"): both are digit strings, so the keys can collide and return the wrong document; `_vb_search` (555-590) mixes matching, ranking, paging and enrichment with a bare `except Exception: continue` (585); `search_legislation` chinhphu branch (508-553) is ~45 lines inline; `_fold` (67) is a local copy; `_clean = _http.clean` alias (62). Three sources in one file: split chinhphu/vbpl/anle. Prefix cache keys. |
| jurisdictions/wto.py | 4 | 4 | 4 | 4 | 5 | 4 | wto.py:301, 353 magic numbers and strings (`exact` regex test; "appeal"/"appellate" note) and the 'v'/'vs'/'—' stopword tuple (303); `_data` global dict plus `time.monotonic()` hand-rolled TTL; get_decision (360-414) is ~55 lines mixing record assembly and rendering. Move stopwords to a constant. |
| jurisdictions/xk.py | 4 | 3 | 3 | 2 | 4 | 4 | xk.py:63-64 `_LABOUR_LAW` alias list and `q = "03/L-212"` (297) hardcode one law's routing; `_MONTHS` (49-59) is a hand-built multilingual table; `search_caselaw`/`search_legislation` signatures lack defaults (178, 287, unlike uz/uy); helpers at the bottom (421+) are used above; `_total`/`_hits` regex scraping; `_LANGS`/suffix dict `{"sq": "", "en": "EN", "sr": "SR"}` built twice (206, 253). Hoist the suffix dict; put helpers before use. |

### Scripts, installers, relay

| module | T | C | E | F | M | S | biggest concrete issue / cheapest fix |
|---|---|---|---|---|---|---|---|
| installer/build.sh | 4 | 3 | 4 | 4 | 4 | 4 | Same file list copied twice (build.sh:24-26 and :38). Loop over one list. |
| installer/fontes_i18n.py | 4 | 5 | 4 | 4 | 4 | 4 | Docstring wraps mid-phrase (fontes_i18n.py:9-11). `_privacy_languages` (:119-125) silently falls back to a missing ../docs/i18n when the list is absent (see fontes.iss). |
| installer/fontes_launcher.py | 4 | 4 | 4 | 4 | 4 | 4 | `APPS` dict has a single entry "fontes"; loops and argv handling (~:180) exist only for it. `cmd.insert(3, "--offline")` (:188) uses a magic index. |
| installer/fontes_setup.py | 3 | 3 | 3 | 4 | 2 | 4 | 645 lines, four jobs: client registry (:89-125), JSONC editor (:176-336), TOML merge (:339-396), CLI/GUI (:467-645). `merge_json` parses twice (:303, :305). Dated claim in `clients()` docstring "checked ... on 2026-11-11" (:99-101). `install()` hardcodes "fontes" while looping `launcher.APPS`. Fix: split editor/merge into a module, drop the double parse. |
| installer/macos/*.command (3) | 4 | 2 | 4 | 4 | 4 | 4 | Three near-identical wrappers (same LOCALES + `. i18n.sh` lines). Comment mismatch with the Windows twin ("Claude Desktop / Codex" vs "Claude, Codex, Cursor, ..."). |
| installer/macos/app-main.sh | 4 | 4 | 4 | 4 | 4 | 5 | Fine; minor only. |
| installer/macos/i18n.sh | 4 | 3 | 4 | 3 | 4 | 4 | Third copy of the language-chain logic; zh/pt aliases hardcoded again (duplicates `_SCRIPT`/`_LEGACY` in fontes_i18n.py). Unavoidable without Python but must be kept in sync by hand. |
| installer/macos/install.sh | 5 | 5 | 5 | 4 | 5 | 5 | Nothing to change. |
| installer/mcpb/localize.py | 4 | 4 | 4 | 4 | 4 | 4 | Top-level script without `main()`. |
| installer/mcpb/manifest.json | 4 | 4 | 4 | 3 | 4 | 5 | Hardcoded tool list and "over 120 jurisdictions" can drift from src; plugin_bundle.py reads this file as its facts source. |
| installer/mcpb/pyproject.toml | 5 | 5 | 5 | 5 | 5 | 5 | - |
| installer/windows/*.cmd (3) | 4 | 2 | 4 | 4 | 4 | 4 | Same wrapper trio duplicated across OSes; Uninstall comment differs from the Mac twin. |
| installer/windows/install.ps1 | 4 | 3 | 4 | 3 | 4 | 4 | Fourth/third copy of the locale chain (install.ps1:11-30); `$alias` hash rebuilt each loop iteration. |
| installer/windows/fontes.iss | 3 | 4 | 4 | 4 | 4 | 3 | [Files] (fontes.iss:22-28) omits privacy-languages.txt that build.sh stages for macOS, so on Windows `_privacy_languages` (fontes_i18n.py:122) finds nothing and the privacy URL is always English. Probable real bug. "Signing slot" comment (:4-5) is speculative. |
| relay/relay.py | 5 | 4 | 4 | 4 | 5 | 5 | Redundant `isinstance(..) and bool(..)` checks; ad hoc `type("H", ...)` handler. Minor. |
| relay/deploy.sh, ecosystem.config.js | 4 | 4 | 4 | 3 | 4 | 4 | Port 4020 hardcoded in both files; final echo "$HOST:127.0.0.1:4020" reads oddly. |
| scripts/brand/gen_brand.py | 2 | 3 | 3 | 3 | 3 | 3 | Dead variant B: MASTER["B"] (:88), SMALL[("B",...)] (:93, :95) with `cut=None` branches; its own comment (:83-85) says kept "only as geometry for reference". `odx=0.0` never non-zero. Debug `print` (:215, :246). Multi-statement lines. Delete variant B. |
| scripts/catalogue.py | 4 | 3 | 3 | 3 | 3 | 4 | Mutable global `L` reassigned in `render` (:27, :134). `_map(code)` rereads JSON per call (:142, :161). `render()` ~60 lines doing everything. Lazy import of coverage_map to dodge a cycle; coverage_map imports private `_score`/`_map`. `_half` (:127) duplicated by readme_tables `_status`. |
| scripts/coverage_map.py | 4 | 4 | 4 | 3 | 4 | 4 | Hardcoded SHORT chip labels; imports private catalogue helpers. |
| scripts/data/countries.NOTICE.txt | 5 | 5 | 5 | 4 | 5 | 5 | No script in the repo regenerates countries.json; the NOTICE only records how it was fetched. |
| scripts/health.py | 4 | 3 | 3 | 2 | 3 | 4 | Hardcoded `PROBES` dict for tr (:42-51) with a "transitional" comment. `skip_reason` parses free-text `s.auth` by regex plus `"fall" not in` (:253-259). Monkeypatches `_http.request` (:66). `_WALL_WORDS` may duplicate src health. Long two-mode `main`. |
| scripts/health_daily.sh | 4 | 4 | 4 | 4 | 4 | 4 | Inline python heredoc repeats diff logic that `health.py --diff` partly has. |
| scripts/launchd/*.plist | 3 | 5 | 5 | 4 | 5 | 5 | ProgramArguments path uses old repo name `/Users/YOU/Development/world-legal-mcp/...` (plist:10). |
| scripts/i18n_check.py | 4 | 4 | 4 | 3 | 4 | 4 | `check()` long; `TRANSLATED_MD`/`REQUIRED_DOCS` hardcoded. |
| scripts/i18n_docs.py | 4 | 4 | 4 | 3 | 2 | 4 | Mixed purpose: string tables, language switchers and the brand favicon/logo block inserter. Hardcoded `REGIONS` (:72-88). `notice` (:67) and `top10` (:91) have no external callers in scripts/tests/src (grep), only possibly internal. `replace_block` (:142) duplicated in readme_tables. |
| scripts/languages.py | 3 | 3 | 3 | 3 | 3 | 4 | `PENDING = ["fr"]` (:46) is stale: fr.py exists in the registry, so the "not in the registry yet" comment and `pending` flag (:113) are dead. Large `main` with nested functions; `TOP10` derivable from `ETHNOLOGUE`; bare `assert`. |
| scripts/linkcheck.py | 4 | 4 | 4 | 4 | 5 | 5 | `anchors(target) if target.exists()` re-checks existence (:66). |
| scripts/no_adapter.py | 4 | 4 | 4 | 2 | 5 | 4 | Large prose data in a .py with no validation against the registry; "Candidate ... not built" entries drift as adapters are added. Move to JSON and validate codes at load. |
| scripts/plugin_bundle.py | 4 | 4 | 4 | 3 | 4 | 4 | Source hosts regex-scraped from adapter source (URL/HOST_CONST); `files()` called three times in `main`; very long line at :100; hardcoded `OWN` hosts. |
| scripts/readme_tables.py | 3 | 2 | 3 | 2 | 3 | 3 | ~240 lines of hand-written override dicts (COV_LABEL, CELL, JUR_NAME, EXTRA_ROWS): README facts live in code, not adapter metadata. Docstring history narration "seeded from the README as it stood on 2026-11-06" (:9). Own `replace_block` (:348) duplicates i18n_docs.py:142. `_status` (:281) duplicates catalogue `_half`. `main` computes `coverage_rows()`/`source_rows()` twice (:357-360). |
| scripts/status_page.py | 4 | 4 | 3 | 3 | 3 | 5 | Python generator carries a ~30-line inline JS blob (:154-184) that re-implements the installer locale chain a fourth time (pt-PT and script logic at :160-161); HTML built by string concatenation in a 90-line `render` (:187-279). Reaches into private `i18n_docs._table` (:142) and `fontes_i18n._SCRIPT/_LEGACY` (:211). `.replace("assets/brand/", "../assets/brand/")` (:215) patches another module's output. Fix: move JS to a data file/template, expose public accessors. Used by health.yml:44. |

### Docs (hand-written)

| module | T | C | E | F | M | S | biggest concrete issue / cheapest fix |
|---|---|---|---|---|---|---|---|
| README.md | 3 | 3 | 4 | 3 | 3 | 4 | README.md ~311-318 filter lists incomplete: nl omits `court`,`area`,`type` (nl.py:709-718), gb omits `date_from`,`date_to` (gb.py:742-743); env-var paragraph omits `WLM_FR_PISTE_SANDBOX`, `FONTES_STATS`, `FONTES_NO_AUTO_UPDATE`, `WLM_HEALTH`; "Why I built this" (143-153) is verbatim docs/WHY.md. Generate filter lists from adapters or point to `list_jurisdictions`. Marker pairs intact. Coverage table showed 123 rows vs 124 adapters: re-run readme_tables.py and check. |
| DESIGN.md | 1 | 3 | 3 | 2 | 4 | 3 | Mostly stale: :44 "adapters return markdown strings" (base.py/models.py return records; ADAPTER_SPEC says never markdown); :46-47 "browser UA" (_http.py sends honest `Fontes/<ver>`); :8 "in-process LRU" (server.py is a 15 min TTL cache, CACHE_MAX 64); :32-33 `us-ca`,`au-nsw` do not exist; :21-30 omits `report_bug`; :49-54 "later phases" already shipped; old `world-legal-mcp` naming. Rewrite in ~20 lines or delete (ADAPTER_SPEC covers the contract). |
| CONTRIBUTING.md | 5 | 4 | 5 | 4 | 5 | 4 | Issue templates and commands verified; no findings that justify a change. |
| CHANGELOG.md | 5 | 5 | 5 | 4 | 5 | 5 | Version/date/counts match pyproject (0.1.1), 124/72 verified. Note: line 52 "Windows version has not yet been run on Windows" will go stale. |
| SECURITY.md | 5 | 5 | 5 | 4 | 5 | 5 | Nothing found. |
| CODE_OF_CONDUCT.md | 5 | 5 | 5 | 5 | 5 | 5 | Unmodified Contributor Covenant; fine. |
| NOTICE | 5 | 5 | 5 | 5 | 5 | 5 | Nothing found. |
| relay/README.md | 5 | 5 | 4 | 4 | 5 | 5 | Retention (730/365 days), env, files match relay.py/deploy.sh/ecosystem.config.js. |
| plugin/README.md | 4 | 3 | 3 | 3 | 4 | 4 | Generated host list (317, count correct) includes namespace/schema URLs never contacted: `a9.com`, `docs.oasis-open.org`, `www.w3.org`, `schemas.openxmlformats.org`, `purl.org`, `www.daisy.org`, `creativecommons.org`; contradicts "A host is contacted only when you ask" (scripts/plugin_bundle.py URL regex scrape). Fix: filter by fetch call sites or an explicit ignore list in the generator. |
| docs/ADAPTER_SPEC.md | 4 | 4 | 4 | 4 | 5 | 4 | :73 two paragraphs merged into one over-long line; helper list omits `_http.error`. |
| docs/CODE_SIGNING.md | 4 | 4 | 4 | 4 | 5 | 4 | Matches installer/windows/fontes.iss and windows.yml; no concrete defect. Contains planning prose for unfinished signing; keep short. |
| docs/FAQ.md | 3 | 4 | 4 | 4 | 4 | 4 | :46-48 "Once the installer is out, it will ask for them" stale: installer ships (README:75, CHANGELOG 0.1.0). Reword. FAQ "apps" section repeats INSTALL.md. |
| docs/INSTALL.md | 3 | 2 | 4 | 3 | 3 | 4 | :106-107 "command `uvx`, argument `fontes`" wrong: package is `fontes-mcp` (everywhere else); `uvx fontes` fetches a different PyPI project. Also the same app lists and uv install commands are repeated in README Quickstart/Install and FAQ. |
| docs/KEYS.md | 4 | 4 | 4 | 4 | 5 | 4 | :70 "36,000 requests an hour" not verifiable in code (api.data.gov limit claim; cite or drop). Env names and DEMO_KEY text match. |
| docs/PRIVACY.md | 5 | 4 | 5 | 4 | 5 | 5 | All numbers (730/365 days, files, env vars) match stats.py and relay.py. |
| docs/WHY.md | 3 | 1 | 5 | 4 | 3 | 4 | Verbatim duplicate of README.md:143-153. Keep one and link. |
| docs/i18n/TRANSLATING.md | 4 | 3 | 4 | 3 | 4 | 4 | :17 and i18n_check.py:83 know three marker pairs but translated READMEs also carry `map:start/end` (docs/i18n/fr/README.md:84, inserted by coverage_map.py:208); say so. Hardcodes rtl list (:22) and tool names (:~64) that already live in languages.json / server. |
| docs/index.html | 3 | 4 | 4 | 3 | 4 | 4 | :31 `"softwareVersion": "0.1.0"` but pyproject.toml:3 is 0.1.1. Counts (124, 72 of 124, 120+) correct. Relative links all exist. |
| docs/compare.html | 4 | 4 | 4 | 4 | 4 | 4 | Counts match (124 adapters, 72). Third-party Moonlit facts dated 18 Nov 2026; unverifiable offline. |
| docs/press.html | 3 | 4 | 4 | 3 | 4 | 4 | :60 "version 0.1.0 on PyPI" stale (0.1.1). :81 "52 are covered only in part" = 124-72, consistent. Links verified. |
| docs/llms.txt | 3 | 4 | 4 | 3 | 4 | 4 | :9 "a Windows installer is on its way" stale: README/INSTALL.md:150/CHANGELOG ship a Windows installer. Other facts (tools, counts, env) correct. |
| research/BUILD_LIST.md | 3 | 2 | 2 | 2 | 3 | 4 | Generated snapshot dated 2026-11-10 (163 rows); no references from code or docs (grep). Courts column is a 45-entry run-on cell (ch row). Mark as generated and give the producing script, or delete. |
| research/SIGNUPS.md | 2 | 3 | 3 | 2 | 2 | 4 | dz note (~:65) "needs `_http` to use the OS trust store (truststore)" stale: _http.py:13,36,65 already uses truststore. Env column says "(to add)"/"(planned)" for `WLM_NZ_LEGISLATION_KEY`, `WLM_KR_LAW_OC`, `WLM_CA_CANLII_KEY`, none exist in src. Mixes permission tracker, open questions and dated session logs ("checked 2026-11-06, 2/3/4"); history narration. Consolidate by jurisdiction or move to per-adapter notes. |
| research/languages.md | 3 | 4 | 4 | 3 | 4 | 4 | "`fr` is counted although its adapter is still being built (`PENDING`)": src/world_legal_mcp/jurisdictions/fr.py exists, but scripts/languages.py:46 still has `PENDING = ["fr"]` (stale code too). "What gets translated" lists README/INSTALL/PRIVACY but TRANSLATING.md also requires FAQ.md and KEYS.md. Counts (80, tier1 12, tier2 68, 7 RTL, 33 non-Latin) match languages.json. |

### Offline tests (tests/)

| module | T | C | E | F | M | S | N | Fn | biggest concrete issue / cheapest fix |
|---|---|---|---|---|---|---|---|---|---|
| test_fr, test_gb, test_bugreport, test_health, test_i18n, test_am_paging, test_nl_filters, test_nl_url, test_mn_paging, test_mm_note, test_mt_search_rank, test_mt_toc_notes, test_intermediates, test_relay, test_plugin_bundle | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | Strong core. gb: negative-only AsyncMock test for "does not claim all words match". intermediates is time-dependent by design (cert expiry); mt_toc_notes has a duplicate import in test_art_regex_tolerates_footnote_asterisk. Fix: none needed. |
| test_registry | 3 | 3 | 3 | 3 | 2 | 4 | 4 | 4 | Mixed bag: citation_to_slug (gb), _http.iso_date/lru_put, toc keyword render, size cap, UA, tzdata. test_zoneinfo_works_without_system_tz only checks find_spec("tzdata") (dependency check). test_discovery_finds_ported_adapters hard-codes the tool list. Fix: move citation_to_slug to test_gb, delete tzdata test, split _http bits. |
| test_installer | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 5 | ~460 lines mixing launcher, config merge, i18n, mcpb manifest, usage question. test_versions_compare_numerically trivial; test_keys_step_links_the_guide pins a URL; test_mac_app_key_prompts_use_dialog_wording pins wording. |
| test_stats, test_update_check, test_status_page, test_server_messages, test_shared_fixes, test_shared_render | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 4 | shared_fixes and shared_render overlap (TOC keyword accent/lists-on-miss in both; zero-header neutral vs test_headers; unknown top-level arg in both :9267 and shared_render:9361). server_messages:9196 uses `A or B` assert (weak). Fix: merge shared_fixes into shared_render. |
| Year-range/filter family: test_bg_year_range, do_year_range, bj_fixes, bs/bt, cn_fixes, lb_fixes, li_fixes, ro_newest, rw_fixes, me_fixes, mz_fixes, ly_fixes, vn_year, sg_year, xk_fixes, uy_dates, tm_fixes | 3 | 3 | 4 | 4 | 4 | 3 | 3 | 4 | Same "range/single/bad" shape rebuilt per adapter with hand-rolled fakes; value is real per adapter but names mislead (do_year_range, bg_year_range test notes/other things). do_year_range: `assert sent == ["impugnacion"] or sent == ["resolución"]` (weak). sg_year:9230 restates a filter spec string. bj_fixes ~1159 has a no-op `.replace("\n\n","\n\n")`. |
| Paging-slice family: am, bb, ec, hu, mn, is_loose_note, pl, mu, sr, us_paging, tw, se, tr (bedesten pages) | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 4 | Good tests (user-felt: wrong page of hits). us_paging, sr, tw, se bundle 3-4 scenarios per test, so failures are hard to localise. is_loose_note name is narrower than content. |
| "Note" tests: ad_status, af_fixes, afchpr_dates, al_fixes, bh_note, co_note, ci_notes, ec_note, ee_fixes, efta_country, echr_phrase, ecowas_fixes, cn_fixes, ht_notes, id_fixes, ie, iq_fixes, jm_note, ly_fixes, lv_court, mg_fixes, mz_fixes, ng_fixes, np_note, no_year_range, pa_fixes, pe_fixes, ph_fixes, pk_fixes, pl_fixes, ps_search_crash, rs_toc, sn_fixes, tt_fixes, uz_fixes, wto_notes, uy_notes | 3 | 3 | 3 | 4 | 4 | 2 | 2 | 3 | Pervasive wording pins: assert substrings of notes ("NOT by decision date", "does not mean", "ONLY", "generic words", "no subject search"). Several restate source constants (see Deletion candidates). Product notes are product output, but pinning them gives churn, not regression protection. Cheapest fix: keep one behavioural note test per adapter (does the note appear under the condition), drop pins on static `notes`/`gaps`/`sources`. |
| Adapter logic fixes (behaviour with fakes): am, ar_search, ba_fixes, bb_fixes, br_artkey, cl_fixes, cr_key, cv_fixes, cv_round3, cz_fixes, de_fixes, dz_arabic, eg_fixes, es_rank, fi_fixes, ge_number, ge_rank, gy_note, hr_fixes, hr_r3, icj_search, icsid_search, in_search, it_query, itlos_main, jp, kg/kh/la, lu_fix1, ma_parse, mc, md, mn_strip, mv_filters, mz, pt_fixes, py_fixes, ro, sc, si_network_error, sk_fixes, sr_fixes, tj_fixes, tt, tw, untc_provision, us_require_terms, uy_notes, vn_nonumber, xk_fixes | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | Real behaviour mostly, but: class-discovery hack (`next(v for v in vars(mod).values() if isinstance(v,type)...)`, `hasattr(mod,"Adapter")`, `X.__new__(X)`) at ad_status:26-41, ba_fixes:745/766/774, bb_fixes:843, icj_search, sk_fixes:9408, jm_note, gy_note, fi_fixes, es_rank, efta_country; manual `orig, mod.fn = mod.fn, fake` try/finally (uy_dates:10442, uy_notes:10489/10507, se_fixes:9108, icj, lv, ro, ps) instead of monkeypatch; inline `import asyncio/pytest` inside test bodies (sn_fixes, tw, tt, vn_nonumber, in_search, iq_fixes, kg). Cheapest fix: export `Adapter = <Class>` in each adapter or use `world_legal_mcp.registry` lookup; one shared fixture. |
| test_it_query | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 2 | test_not_short_citations: `b.get("annoProvvedimento") != "2013" or "numeroProvvedimento" not in b` is mostly vacuous; test_del_with_day has an `or` assert; test_full_date_not_split duplicates a param. Replace `or` with exact body assert. |
| test_ma_parse | 3 | 4 | 3 | 4 | 3 | 4 | 4 | 3 | test_caselaw_year_filter ends in `pytest.raises(Exception)` (any crash passes). Imports mid-file; name narrower than content. |
| test_bh_note | 3 | 3 | 3 | 4 | 4 | 3 | 2 | 3 | Both tests pin wording; one has a weak `or` assert. Candidate to delete the whole file or keep one. |
| test_cl | 2 | 4 | 3 | 4 | 3 | 4 | 2 | 3 | Single uninformative test; belongs in test_cl_fixes. |
| test_ch_search_rank, test_lu_fix1 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | Pin SPARQL text (ORDER BY clause) rather than ranking result; any reformat of the query breaks them with no user effect. lu_fix1 filename narrates history. |
| test_efta_country | 3 | 3 | 3 | 4 | 4 | 3 | 2 | 2 | Negative-only asserts on static notes plus class hack. |
| test_bj_fixes/ci_notes/de_fixes/lb_fixes/pa_fixes | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 2 | try/except/else with a bare `AssertionError` or `except Exception` instead of `pytest.raises`: ci_notes ~1822-1827, de_fixes::test_unavailable_court_message, lb_fixes, pa_fixes. In ci_notes/de_fixes the success path may not be asserted. |
| test_pk_fixes, test_pl_fixes | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 4 | `pk._search_cache.clear()` ~10 times and `pl._laws.clear()` by hand; make an autouse fixture. test_categories_include_general restates CATEGORIES. |
| test_tr | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | Good (recorded fixtures + httpx.MockTransport). Minor: caselaw note test pins "no subject search"/"do not narrow" (:10007); inline imports in later tests; two `_mock`/`bed` setups duplicate. |
| test_ee_fixes/ng_fixes/pa_fixes/eg_fixes/iq_fixes/is_loose_note/lv_court | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | Overlapping tests rebuilding the same rows (ng_fixes 65/75 rows in three tests; pa_fixes texto_unico x2, habeas x2, pinned-code x2; iq_fixes zero-hit x2; is_loose_note x2; eg_fixes cap note x2). |

### Live tests (tests/live/)

| module | T | C | E | F | M | S | N | Fn | biggest concrete issue / cheapest fix |
|---|---|---|---|---|---|---|---|---|---|
| tests/live/test_<code>.py family (about 120 files) | 3 | 3 | 4 | 2 | 4 | 3 | 3 | 3 | Hardcoded dates, counts and source wording that drift: tests/live/test_ad.py:9 (`"2026-32-RE" in a and "Sentència" in a`), test_al.py:37 (`"KOLEGJET E BASHKUARA" ... "2022-11-18"`), test_bb.py:8, test_bd.py:40. Assert structure (non-empty, id round-trips, url), not Albanian/Catalan headings. |
| tests/live/test_conformance.py | 3 | 4 | 4 | 3 | 4 | 4 | 5 | 4 | :119 `test_zz_print_rate_limits` asserts nothing; delete it or move to a script. :21 HTML_TAG is a hardcoded tag list (use an HTML parser or "<" count). :6 docstring mentions "Legacy markdown adapters" but `grep legacy_markdown src` has no hits: stale. |
| tests/live/conftest.py | 5 | 5 | 5 | 4 | 5 | 5 | 4 | 4 | Fine. The repo-root `.env` load duplicates `server.py:508` (load_dotenv), but live tests import server pieces directly so it is needed. |
| tests/live/__init__.py | 5 | 5 | 5 | 5 | 5 | 5 | 3 | 5 | Empty, needed for package imports (tests/__init__.py exists). |
| tests/live/test_mm.py, test_et.py (offline unit tests inside the live tree) | 3 | 4 | 4 | 3 | 2 | 4 | 4 | 4 | test_mm.py:11 `test_mm_label_variants` and test_et.py:11 `test_et_ethiopic_numerals` call pure functions (`_label`, `eth_num`) with no network. They belong in tests/ (offline suite) so CI with `--ignore=tests/live` runs them. Move. |
| tests/live/test_iq.py, test_jo.py, test_bh.py, test_ng.py (direct adapter calls) | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 4 | test_iq.py:7, test_jo.py:7, test_bh.py:9 import adapter classes and `BadRequest` while sibling files go through `server.*`; inconsistent. test_bh.py:9-10 has two imports from `world_legal_mcp.base` on separate lines. Use `server.*` only. |
| tests/live/test_mv.py | 3 | 4 | 4 | 3 | 4 | 3 | 3 | 3 | :6 `pytestmark = pytest.mark.asyncio` is redundant: pyproject.toml:69-71 sets asyncio_mode = "auto". (6 files do this; delete the line.) |

## Verified by hand

- Dead, confirmed by grep: `_http.page()` (no callers; `render.page` is live), `__init__.__version__`
  (no readers), `scripts/coverage.py` (only mentioned in its own docstring).
- Misplaced: `tests/live/test_mm.py::test_mm_label_variants` and `tests/live/test_et.py::test_et_ethiopic_numerals`
  need no network but sit in the live tree, so CI (`--ignore=tests/live`) never runs them.
- Redundant `pytestmark = pytest.mark.asyncio`: 1 file (tests/live/test_mv.py), not 6 as scored.
- Rejected finding: `.dockerignore` entries `.claude`, `status`, `launch`, `.worktrees` are local state
  (status/ is written by scripts/health_daily.sh); keeping them out of the build context is correct.
- Duplication across adapters (AST, identical non-trivial bodies): 12 groups, e.g. `_fold` in bo/cu/gt/hn,
  `_date` in cz/pl/se/si, `get_legislation_toc` in bs/bz/gy. Same-name helpers: 32 `_fold`, 31 `_label`,
  22 `_date`, 21 `_norm_id`, 19 `_norm_provision`.
- Mutation checks (break the line, run the test, restore):

| target | test | result |
|---|---|---|
| `_http.py` VERIFY_X509_PARTIAL_CHAIN | test_intermediates.py | red |
| `us.py` `_require_terms` raise | test_us_require_terms.py | red |
| `us.py` `NOT` stripping | test_us_require_terms.py | red |
| `ch.py` exact SR/abbr first in ORDER BY | test_ch_search_rank.py | **green: not covered** |
| `tr.py` caselaw sortDirection `.upper()` | test_tr.py | red |
| `tr.py` legislation sortDirection `.upper()` | test_tr.py | red |
| `ma.py` year_from > year_to check | test_ma_parse.py | red (but `pytest.raises(Exception)` is broad) |

## Kept on purpose

- Generated, never hand-edited (the generator is what gets scored): README blocks between
  `<!-- coverage/sources/map/languages:start/end -->`, docs/COVERAGE.md, docs/HEALTH.md, docs/status/,
  docs/assets/coverage-map*.svg, docs/i18n/*/COVERAGE.md, research/health/*.json, research/languages.json,
  plugin/README.md host list, .claude-plugin/marketplace.json, plugin manifests.
- docs/i18n/*/README.md, INSTALL.md, PRIVACY.md, FAQ.md, KEYS.md, index.html: prose translations of the
  English files. Not scored; they follow the English source.
- research/maps/*.json and research/*.md source research: reference data for adapters, not code.
- `.dockerignore` local-state entries (see above). `src/world_legal_mcp/intermediates.pem` (certs valid to 2028-09+).
- User-facing notes and warnings inside adapters are product output, judged for accuracy, not as comments.

## Owner calls

1. **Shared adapter helpers.** `_fold`, `_date`, `_norm_id`, docx/PDF parsers and caches are copied across
   adapters (12 identical groups). Moving them into one module is a new abstraction and can change output
   in edge cases. Do it, and if so, in which order?
   → Owner: only byte-identical, context-free ones. Done: 8 groups (17 copies) into `_http`, where
   ADAPTER_SPEC already puts shared helpers. Methods that call module-local functions stay put.
2. **Windows installer privacy link (bug).** installer/windows/fontes.iss `[Files]` omits
   `privacy-languages.txt` (build.sh stages it for macOS), so `fontes_i18n.privacy_url()` always returns the
   English notice on Windows. Fix = ship the file. Behaviour change for Windows users.
   → Owner: fix now. Done (1efc6d3).
3. **English README/doc edits vs 60 translations.** README.md:374 says `pytest -q` runs offline tests but it
   also runs the live ones; README "Why I built this" duplicates docs/WHY.md; filter lists incomplete.
   docs/INSTALL.md:106-107 says `uvx fontes` (wrong package: `fontes-mcp`). docs/index.html:31 and
   docs/press.html:60 say 0.1.0; docs/llms.txt:9 and docs/FAQ.md:46-48 still say the installers are coming.
   Fixing the English leaves translations stale until re-translated.
   → Owner: English + same facts in translations. Done (0661cdf). Translated FAQ prose "once the installer
   is out" still lags (not mechanical).
4. **Version in 6+ places.** pyproject, `__init__`, server.json (x2), plugin.json, plugin/.mcp.json,
   plugin/README.md; nothing checks server.json. Also classifier "3 - Alpha" vs "Fontes is in beta" in
   server.py and README. Which stage word is right?
   → Owner: Beta. Done (58e61bd); plugin_bundle.py now writes server.json versions, `__version__` deleted.
5. **`mcp[cli]` extra** (pyproject.toml): nothing imports mcp.cli or typer. Drop to `mcp`? Packaging change.
   → Owner: drop. Done (58e61bd).
6. **Splitting large multi-source files**: server.py (523 lines, five jobs), tr.py (1304), us.py (1189),
   mu.py (966), fontes_setup.py (645), plus multi-source adapters (ba, bo, ng, pe, icj, hn, es, sn, sc, vn,
   tj). Structural, high churn; worth it?
7. **Live tests that pin source wording, dates and counts** (e.g. test_ad.py:9, test_al.py:37,
   test_mm.py:54) and per-country happy-path tests that repeat test_conformance.py. Per the brief these
   go; that removes a lot of live coverage at once. Delete wholesale, or rewrite to structural asserts?
   → Owner: rewrite to structural checks, delete pure repeats of conformance. Done (57784bb), 539 → 531.
8. **Possible bug in vn.py**: `_texts` cache shared by the vbpl and chinhphu sources with digit-only keys;
   entries may collide (scorer judgement, untested).
9. **tests/live/test_af.py::test_af_search_by_gazette_number fails live** (gazette 1452 no longer finds
   law 1452-16577). Source drift or adapter bug.
   → Neither: since 0.1.0 render.py printed a hit's id only in its Contents line, so af, most ro and
   scanned cv hits showed no id. Fixed (38d5974): such hits get a `get_legislation_text` line. Output change.
10. **ch.py ranking**: exact SR number / abbreviation first in ORDER BY has no test (mutation stayed green).
    Add one?
11. **DESIGN.md** is mostly stale (markdown-returning adapters, browser UA, `us-ca`, "later phases",
    `world-legal-mcp`) and superseded by docs/ADAPTER_SPEC.md. Rewrite short, or delete?
    → Owner: delete. Done (a0d8c72).
12. **Generated output changes**: health.py writes maintainer launchd instructions into every docs/HEALTH.md;
    scripts/languages.py `PENDING = ["fr"]` is stale but feeds research/languages.json; plugin README host
    list includes XML namespace hosts that are never contacted (contradicts "contacted only when you ask").
13. **windows.yml:3** points at docs/RELEASING.md, which does not exist. Write it, or point at CODE_SIGNING.md?
    → Pointed at CODE_SIGNING.md (58e61bd).
14. No CLAUDE.md in the repo (contributors/agents rely on README + CONTRIBUTING + ADAPTER_SPEC). Want one?
    → Owner: tool-agnostic. Done (bc5d96c): AGENTS.md, CLAUDE.md imports it.
15. **tests/live/test_conformance.py::test_toc_and_provision[tw] fails live**: the sample provision
    `第 184 條` (spaces) is not among the TOC labels (`第184條`). Fails identically before round 1. Fix the
    sample, or make provision matching ignore spaces?
    → Matching already ignored spaces (`_nfkc`); only the sample was out of step with the TOC form. Sample
    fixed (e4b0844).

## Rounds

| round | type | modules | before → after | tests |
|---|---|---|---|---|
| 0 | baseline | all | see Summary | 960 passed (offline) |
| 1 | behaviour-neutral: dead code | _http.py; mu, np, pe, tw; scripts/coverage.py (deleted) | _http 333433→444443; mu 233323→333323; np 233344→344344; pe 333323→333333; tw 444344→444444 | 960 → 960 offline; live mu/np/pe green; tw conformance TOC red before and after (owner call 15) |
| 2 | owner calls (approved) | windows installer, packaging, DESIGN.md, AGENTS.md, docs + 79 translations | owner calls 2, 3, 4, 5, 11, 13, 14 closed | 960 → 960 offline; linkcheck, i18n_check clean |
| 3 | bug fixes (approved) | tw sample; render.py legislation hits | owner calls 9, 15 closed; af/tw live green | 960 → 960 offline; render test now requires the id (mutation-checked) |
| 4 | tests | live mm/et pure tests → offline; hk/ba/ccj `or` asserts; mv pytestmark | — | 960 → 962 offline |
| 5 | behaviour-neutral: shared helpers (approved) | _http + 17 adapters, ADAPTER_SPEC | owner call 1 closed (byte-identical only) | 962 → 962 offline; live 164 passed, 6 failed identically on previous code (bo, cu, dz, sn sources) |
| 6 | tests (approved) | 83 live test files; 79 translated FAQs | owner calls 3 (FAQ lag) and 7 closed; live family N/Fn 3→4 | 962 offline; live 539 → 531, error asserts mutation-checked; remaining reds are source-side |

## Appendix: scorer notes (unverified; verify before acting)

#### core: Cross-file notes

- Version string in 6+ places (see pyproject row). One source (pyproject) plus a `--check` that also covers server.json would remove the drift risk; `__init__.__version__` can simply go because `installed_version()` / `_http._VER` already read package metadata.
- Two metadata readers of the version: `_http.py:40-44` (`importlib.metadata.version`, falls back to "dev") and `update_check.installed_version()`; `_http` could call the latter.
- Three places hold the cache directory: `update_check.cache_file`, then `stats.stats_file` and `bugreport.last_error_file` derive from it by `.parent`. Needs one `cache_dir()`.
- `kind_of(method)` (base.py:115) vs `_KIND` + inline ternary (server.py:41, 47): same mapping written twice.
- `page()` exists twice (`_http.py:206`, `render.py:51`); only render's is used.
- `_fetch` is a name in both `_http.py:105` and `server.py:151` for unrelated things.
- Size-limit error crosses modules by wording: created in `_http.py:113` ("too large to read here"), detected by `"too large" in msg` in `server.py:174`. Also `_http.error()` builds "Error (src): ...(HTTP n)." that `server._fetch` strips back off with a regex (172). Round-trip text formatting; a structured error would drop both.
- Time formatting is done four ways: `_http.today`, `stats._today`, `stats.py:108`, `bugreport.py:57`.
- Dated "checked" claims in code comments (`_http.py:6-9`, intermediates.pem:4) are fine in the pem (they say how to refresh); in `_http` they are history and the second one is subsumed by the first.
- Env/key lists (server.json, plugin.json, plugin README, docs/KEYS.md, adapters) are hand-synced; `WLM_FR_PISTE_SANDBOX` is in none of the manifests.
- Product-stage wording disagrees: classifier "Alpha" (pyproject:12) vs "beta" (server.py:209, README.md:679).

#### core: Deletion candidates

- `src/world_legal_mcp/_http.py:206-217` `page()`: `grep -rn "_http.page\|http import.*page" src scripts tests relay installer` returns nothing; adapters call `render.page`-equivalent paths only through server.
- `src/world_legal_mcp/__init__.py:2` `__version__`: `grep -rn __version__` returns only its own definition.
- `.dockerignore` entries `launch`, `status`, `.worktrees`, `.claude`: none exist in the repo.
- `windows.yml:3` reference to `docs/RELEASING.md` (file does not exist): fix the pointer rather than create a doc.
- `health.py:224-246` ops block in `markdown()` (launchd install commands): belongs in a doc, not generated into every report. Not deletion of behaviour, deletion from generated output.
- `mcp[cli]` extra (`pyproject.toml:21`): `grep -rn "mcp.cli\|typer" src` finds nothing; confirm with `uv run fontes --help` after changing to `mcp`.
- `_http.rate_limit_report` is used only by `tests/live/test_conformance.py:121`; keep or move there, low priority.

#### adapters_0: Cross-file notes

- Local HTTP/JSON/status-check helpers re-implemented per adapter: ad `_get`, am `_get`, al `_json`/`_file`, at `_get_json`, afchpr `_api`, az `_api`/`_doc`, bg `_fetch`+5 try/except, bh `_fetch`, bo `_rest`, br (3 try/except). One `_http.get_json(url, source=...)` raising SourceError would remove them.
- Accent folding duplicated: afchpr, al, ar, at `_clean`, ba, bj (inline import), bo (NFD), bh `_norm`. Charset sniffing duplicated: az.py:129 and ba `_decode`. Docx parsers: al.py:83-196 and bh.py:134-192.
- Per-language date parsers not shared: ad `cat_date`, ar `_es_date`, at `_de_date`, bh `_ar_date`, bj `fr_date`, bo `es_date`, bd `_date`, bg `_dash_date`.
- TTL/LRU caches ad hoc: afchpr `_states`/`_advisory`, al `_pages`, at `_toc_cache` (unbounded), bb `time.monotonic` TTL, ba `_registries` and bg `_lists` with mixed-shape keys; only some use `_http.lru_put`.
- Limit/page re-clamped (`max(1, min(int(limit), ..))`) in ba, bb, bd, bj, bo, br although server.py validates; `search_caselaw` signatures without defaults in bg and bj; al re-checks filters (`_check_filters`) though server.py:94 already does.
- `raise SourceError(...)` inside `except` without `from None`: ba.py:181, at, bg.py:200/449, bo, br.py:155/574/614.
- Multi-source files with in-file `# ---` splits: ba (3), bo (3), ad, al, bd, bb. Separate callers exist for the parts, and ba/bo are 790-820 lines.
- Data hardcoded in code: am constitution ids, ar `_ALIASES`, bd `_SUPERSEDED`/`_EN_BN`, bj `loi-2018-16`, bg `_CONST_HIT`, ba `CONST_*`, br `_ALIASES`.
- `as_of=_http.today()` as fake version date: at, bd.
- Private cross-module access: af -> `_http._throttle`/`_http.stats` (no other users); bb -> `_ccj._rows`/`_ccj._key`; gy.py:309 -> `bb._pdf_origin`.
- History narration in docstrings: ar.py:4,10; ba.py:41; br.py:4.
- Positive: au.py is the cleanest; its import style differs from the rest.

#### adapters_0: Deletion candidates

- ad.py:618, 629: `pre` assigned/accumulated, never read.
- al.py:237 `_check_filters`: server.py:94/323/380 already validates declared filters. al.py:595 `archive_year` check is unreachable (search_caselaw returns at al.py:553).
- afchpr.py:260-265: `for ... break` loop in `_row`.
- at.py:74 stale comment; at.py:85/95 `_clean`/`_iso` (duplicates of `_http.clean`/`_http.iso_date`).
- bd.py:540: `for el in pre[:1]` loop.
- bg.py:427: no-op list comprehension; bg.py:71 alias `_clean`.
- bh.py:51: duplicate month key; bh `_TYPES` values (only keys used, bh.py:453-456); bh.py:195 noqa hack.
- bj.py:76: `arrete` alternative in `_LAW_ID` and gaps entry bj.py:342 (search never queries it).
- bo.py:755-762 `_scan_lx`: trivial re-raise wrapper.
- br.py:71 `_SKIP` single-member set (inline).
- Relocate, not delete: bb.py:168-245 CCJ helpers to ccj.py (callers: bz.py:48/537, gy.py:38/292/309).
- Not dead (verified): `al` S3 host in `min_interval` is used (al.py:525); `bd._EN_BN`/`_SUPERSEDED` are used (bd.py:419, 465).

#### adapters_1: Cross-file notes

- PDF download with HEAD size check and a private size constant is reimplemented in bs.py:96, bz.py:404, ci.py:127, cm.py:239, cv.py:154 (`MAX_PDF = 40_000_000` identical in bs/bz/ci/cm/cv at bs.py:59, bz.py:58, ci.py:71, cm.py:40, cv.py:72), cu.py:66 (`MAX_BYTES`), and ccj.py:282 has no cap at all. Grep also shows the same constant in ~15 other adapters outside my list. One `_http.pdf_get(url, max_bytes)` would remove all of them.
- Accent-fold helper copied in ci.py:92, cu.py:103, cv.py:99, do_.py:93, dz.py:76; `_http` has none. Add `_http.fold`.
- Month-name tables and date parsers per adapter: cl.py:56, cm.py:49, cu.py:94, cv.py:88, do_.py:47, dz.py:62 (+ dz.py:502), de.py:221-228. `_http` has `en_date` only.
- Provision-label normalisers with the same job and different names: bs.py:468, bz.py:369, ci.py:249, cv.py:492, ca.py:422, cm.py:347, cz.py:196 (`_norm_prov`/`_norm_provision`), co.py:227, cr.py:100, cl.py:147, dk.py:53, de.py:273 (`_key`).
- Retry-once-on-network-error is hand-written in cn.py:48, co.py:120, cu.py:266, cz.py:116; with dated "health run 2026-11-10" history comments in cn.py:49, co.py:120, cz.py:117. A retry option on `_http.get` would remove all four.
- Hardcoded data tables in code: cz.py:46-100 `_COURTS`, cr.py:191 `BASE_CODES`, cu.py:74 `_EDITIONS`, cv.py:515 `SCANNED_LAWS`, bs.py:88 `_CONST_SUBJECT`, ci.py:89 `_LABOUR`, dz.py:58 `_CC_CATS`, de.py:55 `_NON_BFH_RE`.
- Signature drift: dz.py:663 and :718 and de.py:449 declare `limit, page, filters` with no defaults (dz also crashes on `filters=None`); the others default them. Check against base.py whether the caller always passes all three; if so the defaults elsewhere are noise.
- `rate_limit` strings share the "unknown; 1 s spacing, no 429 seen in ~N requests (2026-11)" template (difc, dk, do_, dz, ec, echr). Accurate per adapter, but it records the test run rather than the source's limit.
- Several adapters embed dated verification history in docstrings and gaps (cu.py docstring, dz.py:640-651, ec.py gaps "2026-11-10", do_.py "verified 2026-11-06"). Dates on facts about a source are information; narration of health runs is not.

#### adapters_1: Deletion candidates

- cv.py:655 `else list(STJ_SECTIONS)` branch: dead, inside `if section:` at cv.py:654 (the full-list loop is at cv.py:340). Delete the conditional expression and loop over `[section]`.
- de.py:251-253 `x.tag = "div" if x.tag == "Content" else x.tag`: assigns the tag to itself for every non-Content element; verify the intent and delete or make it an `if`.
- ca.py:305 local `text()`: check whether `_http.text` (_http.py:187) can replace it; if equivalent, delete.
- dk.py:255-256: `dtype` and the second `.lower()` computation, merge into one.
- Dated "health run" comments cn.py:49, co.py:120, cz.py:117: delete (commit history holds it).
- Nothing else in my files is unreferenced code; each adapter class is registered by its module.

#### adapters_2: Cross-file notes

- Accent-folding helper is copy-pasted as `_fold`/`_plain` in ecowas:78, es:99, fr:214, gr:77, gt:79, hn:68, ht:66, icsid:54 (and ~15 more adapters; `grep -n "def _fold" jurisdictions/*.py`). `_http` has no fold. One `_http.fold` would remove them all.
- `_title_rank` duplicated in gb.py and ge.py. ISO date validation duplicated in fr (:172, :405), ge (`_check_iso`), icj (`_DATE`), icsid (`_DATE`), hr (:193), hu (`_year`).
- `_http.today` is bypassed in es (`_today`, :89) and eu (:618).
- limit/page clamps are repeated in nearly every adapter (ecowas :512/:555, efta, icj, icsid, hr, ht), with differing caps (50/100/200); hu and gy don't clamp.
- "not researched yet" / "works but not built" appear in gaps for ee, eg, et, fi, gb, ge, gr, hu, icj. These are TODO text, not gaps a user can act on.
- Dated research logs in docstrings (fr, ge, gt, gy, hn, hr, ht) duplicate the `gaps` tuple and `research/*.md`. They are history narration; keep only how the source behaves.
- PDF paragraph-reflow / article splitting is reimplemented in gt, hn, gr, ht (`_paras`), and gy (`_split` "adapted from bs.py/tt.py").
- gy reaches into private functions of ccj/bb; hk carries a general ZIP reader; icj and ecowas/es/fi/hn bundle two sources each.
- Hardcoded name/label tables (gb `_COURT_LABELS`, icsid `_STATE_STYLE`, eu `_STEMS`, ecowas kinds, icj `_STOP`) are data in code; acceptable if they live in a data module, but they are unvalidated.

#### adapters_2: Deletion candidates

- ge.py:38 `_UNSUP`: `grep -rn "_UNSUP" src` shows no use in ge.py beyond the definition (ee.py has its own live copy).
- icj.py `_LAWS` third element (keyword string): only ever unpacked into `_` (icj.py:268 and search_legislation); delete the member.
- hk.py `_size` unused tuple element (:180, :189).
- hr.py:312-315 `is_usrh` conditional (always true after the filter at :309).
- ecowas.py:214 redundant f-string wrapper.
- fi.py:611 `want = None` (redundant assignment).
- gb.py module-level `_get_judgment/_get_toc/_get_provision/_get_text`: one-line delegations from the class methods; inline them.
- eu.py:105 `_clean`: duplicates `_http.clean`. es.py:89 `_today`: duplicates `_http.today`. eu.py:89 stale "candidates for promotion" comment.
- Docstring research logs: gt.py:4-21, hn.py:4-33, fr.py:1-32, gy.py:20-25, ht.py:22-31 (history; facts already in gaps/research).
- ht.py `fr_date`/`norm_provision`: public but no callers outside ht.py (grep over src and tests).

#### adapters_3: Cross-file notes

- Hand-built `SourceError("... HTTP {status}")` / `Error (X): ...` strings sit beside `_http.error(...)` in the same module: id, ie, it, jm, jp, li, lu, lv, ly (:239, :278, :281, :284, :613), mc (:106, :156), md (:164). One format would give the client a consistent error shape.
- Two-source adapters packed in one file: id (JDIH + MPR UUD), ie (eISB + LRC + Constitution), il (Knesset + gazette PDF + Wikisource), in_ (India Code + SC), li (Lilex + OGH), lu (legislation + ZIP case law), ly (MoJ + Supreme Court), jm (JCPC/CA/SC). These are the main M findings; the splitting candidates with separate subsystems are lu, ly, il, ie.
- Per-module private caches with different policies (`_cache`, `_law_cache`, `_docs`, `_ca_cache`, `_list_cache`, `_pdf_cache`, `_pages`, `_const_cache`, `_res_cache`): some size-capped via `lru_put`, some TTL (ly `_TTL`, lu 1800), some unbounded (li `_ogh_index`, kh `_list_cache`). A shared helper would remove ~10 near-duplicates.
- `limit = max(1, min(int(limit), 50))` and `YYYY` year-regex validation repeated in iq, kh, ly, ma (twice), md, mc, la (raises instead of clamping, la.py:170).
- Provision-label normalisers re-implemented in jp, kh, lb, lu, li, ly (_label), ma (_norm_prov), mc (_norm), md (_art_label).
- Tuple/dict-of-strings data models instead of dataclasses: lb (5-tuples), li (law dict), lu, il (_gazette_doc 5-tuple), ie (_Doc), ma (_law 5-tuple), ly (_ruling dict), md (blocks).
- Docstring, notes, warning and gaps state the same fact repeatedly (la scans-only x4, kh, jo outage x2, kg, ly gaps vs "Not used", ma gaps vs docstring, md gaps vs docstring). Source-quirk detail is information, but the repeats are not.
- History narration in comments/docstrings: la.py:84-85, :119-120; jo.py:22-26; lu.py:25; ly docstring "verified 2026-11-10" blocks.
- Bare `except Exception` swallowing: il.py:167, :181; id.py:563 (`pass`); lv.py:137; la.py:88; ly.py:245; md.py:364.
- `_http.today()` exists (_http.py:306); md.py:395 uses `date.today()` directly. li.py:402 needs dd.mm.yyyy so is not a straight duplicate.
- Hardcoded heuristics where data would do: kg._stem, is_._stem, itlos stop-words, lb._locate number spellings, ly ordinal tables (domain data, tolerable).

#### adapters_3: Deletion candidates

- kh.py:158 second return value of `_parse` (evidence: callers at kh.py:294, :306, :318 all do `marks, _ = _parse(lines)`): return only marks.
- lb.py:257 `legislation_filters = {}`: identical to the base default (base.py:88 `legislation_filters: dict[str, str] = {}`).
- in_.py:237-239 unused walrus bindings (`m` never read).
- iq.py:370, :390 `as_of=""` (default value).
- jp.py:80 `_child` wrapper (5 uses, all replaceable by `el.find`); low value, optional.
- jo.py:22-26 and :243-245 outage narration; lu.py:25 "added 2026-11" line; la.py:84-85 and :119-120 history comments: delete the history, keep the one-line reason.
- ly.py gaps/notes duplicates of the docstring "Not used" section; ma.py/md.py gaps repeating docstring.
- md.py:84 `_clean = _http.clean` alias (use `_http.clean` directly or a normal import).
- id.py:469 discarded third return of `_structure`.
- Note: id.py:396 `hit_words` is a nested helper used at :409, not dead.

#### adapters_4: Cross-file notes

- Local PDF/HTML helpers duplicating `_http`: ng `_pdf_text` (188), mz `_pdf_text` (188, with a font-shift variant), nl `_html_to_md`/`_clean_md` (121-131), pk `_strip`-style helpers, ph `_strip_tags` (143).
- Hand-rolled caches instead of `_http.lru_put`: nl `_toestand_cache` (578), ng globals, pk `_shortened` (78) and `_ihc_meta` (271), no TTL sitemap (43, 70), pt `_CODE_NAMES` as a one-key dict.
- Duplicate definitions inside one file: mu `_despace`, np `_score`, pe `_NAMED_LAW`.
- Inline month tables rather than `_http.en_date`/`iso_date`: pa, pe, ph, pk, mz, no, pt (84), and Portuguese/Arabic ones where no helper exists.
- `search_*` signatures: nl, no, np, mm, mz have no defaults while ng, pa, pe, ph, pk, pl, ps, pt do.
- Helpers or constants defined after first use: pe, pa `_type` (199), mg `_ART`, no `_num_slug`, pl `_top_units`/`_depth`.
- Odd `gaps` continuation indentation: me, ng, no, np, pl (457-466).
- Query-triggered hardcoded notes/special cases: mg, pa, pe, ng, pt (604-625).
- Redundant `legislation_filters = {}`: mg:308, pt:408 (check the base class default before removing).
- Stale/volatile counts and dates baked into notes: ng, mm, mu.
- Long `search_*` methods mixing validation, paging and note text: mz, ng, nl, no, np, pa, pe, pk, ps, pt.
- Multi-source adapters that exceed the ~300-line threshold with separate sub-jobs: mu (966), pe (817), ng (697), pt (713), pl (679).

#### adapters_4: Deletion candidates

- mu.py:227-264 dead `_despace` (shadowed by the def at 457), plus `_PREFIXES`/`_SUFFIXES` (267-269) and the inner `Counter` import (232); verified by grep: the live `_despace` at 457 uses `collections.Counter` and neither set.
- np.py:67-84: `_SUFFIXES`, `_stems`, first `_score` (82; shadowed by 87). `RERANK_WINDOW` (66): grep finds no other use in np.py.
- pe.py:269 (or 87): identical duplicate `_NAMED_LAW`.
- mg.py:308 and pt.py:408 `legislation_filters = {}` if the base class already defaults to empty.
- mt.py:255-256 `elif over: pass`.
- nl.py `_KINDS` identity map (95); `_html_to_md`/`_clean_md` (121-131) if `_http.html_to_md` suffices.
- ng.py:188-206 `_pdf_text` (use `_http.pdf_text`); mz.py:188-195 likewise unless the font-shift hack is needed (then move it into `_http`).
- pk.py: fold mixin `_PakistanCodeLegislation` into `Pakistan`; delete the stale TLS docstring text (1-3, 279-287).
- me.py:81 `_this_year` wrapper; the OLE2/.docx parser (116-220) if no other adapter needs it (the grep for other users returned nothing in the sandboxed shell; re-run to confirm).

#### adapters_5: Cross-file notes

- No shared get-or-raise-SourceError helper. Each adapter hand-rolls its own HTTP/JSON wrapper: si `_json`, sk `_get`/`_json`, tm `_fetch`/`_json`, tj `_json`, sn `_json`, sr `_post`, uy `_impo_json`/`_decode`, tt `_dll_get`, tr `_bpost`/`_aym_post`/`_gib_post`, uz `_fetch`, vn `_vc_post`/`_al_get`, xk `_api`/`_gzk_get`, wto `_fetch`. One `_http` helper (status check, error text, optional JSON parse) would remove most of these.
- `_fold` (diacritic folding) is copied in py, ro, rs, sn, sr, tr, uy, vn, xk (each slightly different: xk uses NFKD ascii, vn also replaces đ). A shared `_http.fold` would serve all.
- Hand-rolled caches and TTLs differ everywhere (`lru_put`, `time.monotonic`, `time.time`, one-key dicts like vn `_al_index`/`_vb_index`, wto `_data`). A shared TTL cache helper would remove about a dozen variants.
- Month tables and date parsers recur: untc `_MONTHS`, xk `_MONTHS`, py, ro, sc, sn, sr, tj. `_roman` is copied in untc and us.
- Tag-strip regex `<[^>]+>` recurs in si, tj, tr, tt, uy, vn, xk and others, usually followed by `html.unescape` and `clean`; a shared `_http.strip_tags` would fit.
- Pagination slicing `(page-1)*limit` is repeated in nearly every adapter; tr has a good `_paged` helper that others do not use. Signature defaults are inconsistent: tt, untc, uy, uz, vn, wto have `limit=10, page=1, filters=None`; tw, us, sn, tr and xk use bare `*, limit, page, filters`.
- Untyped dict "law" records in sr, tj, tt, untc, us, uy, uz and vn; positional tuple caches in sn, tm and tj. Small dataclasses would make these self-documenting.
- Dated "(2026-11-xx)" narration in docstrings, `gaps`, rate_limit strings and comments (si, sn, tr, tw, uy, tt, uz, vn, xk). The `rate_limit` strings are product metadata and are acceptable; the code comments and docstring "Code unchanged" notes are history narration.
- Hardcoded court, type and special-law tables recur (se, sg, tw, tr, tt, uy, xk, us). Where they are lookup facts of the source they are acceptable; special-case ids in search code (py 9580, tt `u120718`, tr 2709, xk 03/L-212, sc 1979 slug) are data hidden in logic.
- Large multi-source files that are split only by comments: tr (1304), us (1189), sc (795), tj (548), sn (620), vn (707). Each has separate per-source callers inside one class, so these are the strongest candidates for the M criterion.
- Gotcha docstrings (si, sn, tr, uz, vn, xk, wto) are information, not slop. The slop in this batch is limited to history narration, a few restating comments and the repeated caveat strings (tw notes vs `_AMEND_NOTE`).

#### adapters_5: Deletion candidates

- tw.py:211, 230 `_Law.order`: written, never read. Verified by grep (only those two lines).
- tm.py:425 unused unpacked `date`.
- rs.py:322 unused `lat` title; rs.py:351 unused loop variables.
- ro.py:58 `_clean = _http.clean` alias; ro.py:167 trivial `_text` wrapper; sk.py:166 trivial `_label` wrapper; vn.py:62 `_clean` alias.
- sk.py:150 redundant `isinstance` check.
- tt.py:685 redundant `as_of = ""` and 676 copy comprehension.
- untc.py:541-544 redundant `exact=""` assignment inside try/except.
- sg.py:211 `Results[DecisionHit]` annotations (no other adapter uses them).
- si.py:25-29 and 296-297 dated outage narration ("Code unchanged").
- sn.py:30, 42 history narration ("added 2026-11-10").
- Duplicates to merge rather than delete: sn `_PDF_ART`/`_ART`, us `_roman` vs untc `_roman`, uy `_fold`/`_tags` vs `_http`.

Note: findings for py, ro, rs, rw, sc, se, sg, si, sk, sn, sr, tj, tm were recorded from the first reading pass; line numbers are as read and not re-verified after the summary.

#### tooling: Cross-file notes

- Locale chain (language tag -> fallback list, pt-PT, script aliases, zh) is implemented four times: installer/fontes_i18n.py, installer/macos/i18n.sh, installer/windows/install.ps1:11-30, scripts/status_page.py:157-164. Drift risk is real; at minimum a test should compare outputs.
- `replace_block` exists twice (scripts/i18n_docs.py:142, scripts/readme_tables.py:348) and catalogue `_half` vs readme_tables `_status` are the same idea.
- `installer/fontes_i18n.py` also ships in the wheel as `world_legal_mcp/_fontes_i18n.py` via force-include (pyproject.toml:65). The copy exists only at build time, so the source file is the only one; no duplication in git.
- Windows installer gap: build.sh stages privacy-languages.txt; fontes.iss does not (fontes.iss:22-28). Windows users always get the English privacy URL.
- Generators depend on each other's privates: catalogue <-> coverage_map (lazy import to avoid a cycle), status_page -> i18n_docs._table and fontes_i18n._SCRIPT.
- Hand-written facts in code rather than data: health.py PROBES, readme_tables overrides, no_adapter.py, languages.py ETHNOLOGUE/TOP10, coverage_map SHORT, plugin_bundle OWN hosts, manifest.json tool list.
- Three wrapper scripts per OS differ only by action; the Mac and Windows comments describe the supported clients differently.
- Stale repo name: scripts/launchd plist still says world-legal-mcp; docs/HEALTH.md:252 says health_daily.sh writes status/ while health.yml now commits docs/status/ (both exist, but two paths for the same page is confusing).

#### tooling: Deletion candidates

- scripts/coverage.py: no callers. `grep -rn "coverage\.py"` finds only its own docstring (coverage.py:3); coverage_map.py replaced it.
- scripts/brand/gen_brand.py variant B (MASTER["B"] :88, SMALL[("B", n)] :93-95, all `cut is None` branches, `odx`/optical_dy that is always 0): its own comment says it is reference geometry only. The script itself is referenced only from .gitignore:17 and its docstring; it is a manual tool, keep but trim. Remove the debug prints (:215, :246).
- scripts/languages.py `PENDING = ["fr"]` (:46) and the `pending` flag (:113): fr is already in the registry (src/world_legal_mcp/jurisdictions/fr.py exists).
- scripts/i18n_docs.py `notice()` (:67) and `top10()` (:91): no references outside the definitions in scripts/, tests/ or src/ (grep for `i18n_docs.notice|top10` returns nothing); confirm internal use before deleting.
- Installer: no outright deletions; the "Signing slot" comment in fontes.iss:4-5 is speculative and can go.

#### docs: Cross-file notes

- Package name drift: INSTALL.md:106-107 `fontes`; every other doc and pyproject use `fontes-mcp`.
- Version drift: pyproject 0.1.1, CHANGELOG 0.1.1, but docs/index.html:31 and docs/press.html:60 say 0.1.0. Derive from pyproject in a generator or drop the number.
- Windows installer status: llms.txt:9 "on its way" vs README:75, INSTALL.md:150, CHANGELOG.
- Installer status: FAQ.md:46-48 "once the installer is out".
- Duplication: WHY.md vs README:143-153; app lists and uv commands across README, INSTALL.md, FAQ.md, index.html.
- DESIGN.md contradicts ADAPTER_SPEC.md (markdown vs records, UA, cache) and README.
- Generated-block markers are intact in README.md and in docs/i18n/fr/README.md (checked; map, languages, coverage, sources). `.github/workflows/windows.yml:3` references nonexistent `docs/RELEASING.md` (outside list).
- Relative link and path sweep over all 16 .md docs found no broken links; html pages only the `mailto:` false positive.
- Counts verified consistent: 124 adapters (108+4+1+11), 72 covered, 80 languages, 7 tools plus `report_bug`.

#### docs: Deletion candidates

- docs/WHY.md: duplicates README.md:143-153 (diff identical); check inbound links with `grep -rn WHY.md .` before removing.
- DESIGN.md: stale in most sections and superseded by docs/ADAPTER_SPEC.md; rewrite to a short page or delete.
- research/BUILD_LIST.md: dated generated dump, no inbound references (grep over repo found none outside research/).
- research/SIGNUPS.md session-log sections ("checked 2026-11-06, 2/3/4") after folding into one table.
- `scripts/languages.py:46` `PENDING = ["fr"]` (fr adapter exists), with the matching sentence in research/languages.md.

#### tests_offline: Cross-file notes

- Class discovery is guessed in ~12 files (listed above); adapters should expose a single canonical class name or tests should use the registry. This is the single biggest cross-file smell.
- Manual monkey-patching by `orig, x = x, fake` + try/finally (uy_dates:10442, uy_notes:10489-10513, se_fixes:9108-9171, icj, lv, ro, ps, id, in_) is repeated where `monkeypatch` is already used in neighbours; leak risk if an assert is before the finally (they use finally, so safe, but noisy).
- Cache clears by hand: pk, pl, tr (twice), untc_provision (`untc._chapters.clear()` plus `__import__("time")` at :10258), ps. Use autouse fixtures.
- try/except/else raising AssertionError (ci_notes, de_fixes, lb_fixes, pa_fixes; also se_fixes:9125-9128 where the test passes silently if nothing is raised) instead of `pytest.raises`.
- se_fixes::test_hovratt_group_and_court_names_in_error: the except branch is only asserted if BadRequest is raised; if the adapter stops raising, the test stays green.
- Inline imports (`import asyncio`, `import pytest`, adapter symbols) inside test bodies in ~20 files; redundant `@pytest.mark.asyncio` in icj_search/rs_toc while asyncio auto mode is on (shared_fixes, stats, tr rely on auto mode).
- Year-range and paging-slice tests are reimplemented per adapter with near-identical fake shapes; a parametrised shared helper would cut hundreds of lines but only if adapters share a base hook (they mostly do not).
- Wording pins dominate "note" tests; they also restate `notes`/`gaps`/`sources` class constants (see below).
- Time-dependent: ar_search (current year), fi_fixes, intermediates (cert expiry; intended), relay/status_page use fixed dates (fine).
- Overlap between shared_fixes and shared_render (TOC keyword, header, unknown args).
- test_stats and test_update_check have the same cache fixture shape; fine.
- test_registry belongs partly in gb and _http tests.

### File naming inconsistency / mixed files
- History or round naming: test_lu_fix1.py, test_cv_round3.py, test_hr_r3.py, test_cl.py (vs test_cl_fixes.py).
- Misleading or too-narrow names: test_br_artkey, test_cr_key, test_bg_year_range, test_do_year_range, test_dz_arabic (has an empty-query test), test_is_loose_note (merged paging too), test_ma_parse (caselaw year, error naming), test_mn_strip (strip, date range, decision date, search note), test_ro_newest, test_ps_search_crash (also `_missing_words`), test_registry (mixed).
- Split-per-adapter siblings that should merge: au/au_label, bb/bb_fixes, cl/cl_fixes, cv_fixes/cv_round3, cz/cz_fixes, ec/ec_note, ge_number/ge_rank, hr_fixes/hr_r3, hu/hu_fixes, shared_fixes/shared_render, uy_dates/uy_notes (both test uy search), vn_nonumber/vn_year.
- Convention: `test_<code>_fixes.py` vs `test_<code>_<topic>.py` vs bare `test_<code>.py` all coexist.

#### tests_offline: Deletion candidates

Restates constants / pins static strings (delete):
- test_ie::test_notes_point_to_wrc_for_employment_decisions (restates `Ireland.notes`)
- test_iq_fixes::test_status_translated (restates `_STATUS`)
- test_itlos_main::test_basic_texts_pointer_in_notes_and_gaps
- test_jp::test_courts_source_listed and ::test_case_law_source_listed_first (restate `sources`, overlap each other)
- test_kh_fixes::test_criminal_code_listed_as_not_covered (restates `gaps`)
- test_lu_fix1::test_notes_say_case_law_is_cassation_only
- test_lv_court::test_legislation_gap_points_to_likumi_lv
- test_ly_fixes::test_missing_codes_listed and the `"date_from" in Libya.caselaw_filters` assert
- test_no_year_range::test_legislation_gap_gives_lovdata_url
- test_pe_fixes::test_constitution_has_no_gazette_warning
- test_pk_fixes::test_categories_include_general
- test_pt_fixes::test_date_window_is_tight_enough_to_stay_on_topic (asserts `_DATE_WINDOW <= 20`)
- test_in_search::test_india_legislation_refusal_names_manual_route
- test_sg_year::test_year_spec_says_single_year and ::test_no_legislation_pointer_names_sso (constants)
- test_wto_notes::test_agreement_texts_pointer (asserts class `notes`/`gaps` only)
- test_tw_fixes::test_court_filter_maps_and_keys last assert (`"court" in j.caselaw_filters`)
- test_ad_status, test_af_fixes (88/101/153), test_afchpr_dates (3 gaps tests), test_al_fixes::test_generic_unifying_words_known, test_co_note::test_notes_upfront, test_do_year_range::test_notes_lead_with_legislation_pointer, test_ee_fixes::test_provision_says_no_dated_wording, test_efta_country::test_efta_states_no_legislation_plainly, test_echr_phrase unsupported-legislation test, test_ecowas_fixes::test_legislation_gap_names_court_basic_texts, test_cn_fixes::test_legislation_gap_points_to_official_site_for_manual_use, test_ht_notes::test_warning_does_not_claim_nationality_law, test_bh_note (both), test_registry::test_zoneinfo_works_without_system_tz, test_installer::test_versions_compare_numerically.

Duplicates:
- test_af_fixes::test_hits_offer_no_contents_line duplicates test_old_gazette_hit_has_no_contents_offer
- test_cv_fixes legislation-note test duplicated by two cv_round3 tests
- test_ecowas_fixes::test_hit_snippet_warns_about_scans subsumed by test_hit_shows_scan_status
- test_eg_fixes: two cap-note tests; test_ci_notes: two overlapping note tests
- test_hr_fixes and test_hr_r3 both assert `Croatia._status`
- test_iq_fixes::test_zero_hit_phrase_note vs test_zero_hit_says_not_found_and_year_note_counts_languages
- test_is_loose_note::test_note_says_when_no_hit_mentions_term vs test_no_confirmed_match_leads_the_note
- test_it_query::test_full_date_not_split (param of test_not_short_citations)
- test_pa_fixes: test_texto_unico_first vs test_texto_unico_filter_puts_code_title_first; test_habeas_corpus_says_none_found vs test_search_notes_civil_code_and_habeas; test_codigo_fiscal_pinned / test_codigo_de_trabajo_pinned
- test_pl_fixes::test_no_article_pdf_says_id_is_not_an_act vs test_pdf_act_without_articles_says_so
- test_ps_search_crash::test_incomplete_note_leads vs first test
- test_ng_fixes: three tests over the same rows
- test_shared_fixes::test_toc_keyword_accent_insensitive_and_lists_on_miss, ::test_stray_top_level_arg_points_to_filters overlap shared_render equivalents
- test_cl.py: delete or fold into cl_fixes.

#### tests_offline: Not functional

- test_bh_note: `or` assert makes one check pass if either wording exists.
- test_do_year_range: `assert sent == ["impugnacion"] or sent == ["resolución"]` passes for either of two outputs, the second possibly a regression.
- test_it_query::test_not_short_citations: `!= "2013" or "numeroProvvedimento" not in b` is true for most params whatever the code does.
- test_it_query::test_del_with_day: `or` assert.
- test_ma_parse::test_caselaw_year_filter: `pytest.raises(Exception)` accepts any crash (including a NameError).
- test_us_require_terms::test_negation_only_rejected: `pytest.raises(Exception)`, same; also "a b" is rejected for being single-letter, not negation.
- test_tw_fixes::test_chinese_court_name_and_bad_court, ::test_search_caselaw_fetches_source_pages_and_slices: `pytest.raises(Exception, match=...)` (match saves it; acceptable) -- but test_tw_fixes::test_constitution_provision_carries_amendment_note only checks two substrings with a fake `L` and fake loader.
- test_ci_notes (~1822-1827), test_de_fixes::test_unavailable_court_message, test_lb_fixes, test_pa_fixes: try/except/else patterns where a missing raise or a different exception can pass or yield a bare AssertionError.
- test_se_fixes::test_hovratt_group_and_court_names_in_error: `try: ... except BadRequest: assert` with no else; stays green if nothing is raised.
- test_server_messages::test_unsupported_names_only_matching_sources: `"e-Gov" not in ... or "courts.go.jp" in msg` is an `or` assert.
- test_xk_fixes::test_labour_law_name_routed_to_number: `"03%2FL-212" in urls[0] or "03/L-212" in urls[0]` accepts either encoding (fine) but the second assert only checks the note.
- test_icsid_search `_run` returns None if class missing (guard hides a missing class; then asserts on None would fail, but check the helper).
- test_gb::test_search_note_does_not_claim_all_words_match: negative-only against AsyncMock.
- test_lv_court, test_efta_country, test_ht_notes, test_pe_fixes: negative-only asserts on static constants (stay green if the code path that builds the note is never reached).
- test_wto_notes::test_agreement_texts_pointer, test_registry::test_zoneinfo_works_without_system_tz: no behaviour exercised.
- test_si_network_error, test_tt_fixes: substrings of an error built in the same code under test, with mocked transport; acceptable but mock-heavy.
- No skip/xfail markers found in the offline files read.

#### tests_offline: 5 tests to mutation-check (break the source line, expect a red test)

1. test_intermediates (PARTIAL_CHAIN regression): comment out `ctx.verify_flags |= ssl.VERIFY_X509_PARTIAL_CHAIN` at src/world_legal_mcp/_http.py:73. Test must fail.
2. test_us_require_terms::test_negation_only_rejected / test_rejected: weaken the check at src/world_legal_mcp/jurisdictions/us.py:377 (e.g. `len(w) > 0`, or drop the NOT-strip at :374). Broad `Exception` may still hide the wrong failure.
3. test_ch_search_rank (ORDER BY pin): change the tie-break in the ORDER BY at src/world_legal_mcp/jurisdictions/ch.py:566 (e.g. drop `DESC(STR(?sr) = exact ...)`); check that the test fails on the semantics, not just the text.
4. test_tr::test_bedesten_sort_breaks_ties_and_sends_capital_direction: change `_SORTS[sort].upper()` to `_SORTS[sort]` at src/world_legal_mcp/jurisdictions/tr.py:739 and :1183; both asserts (sent[0], sent[1]) should fail, plus break the `sortFields` tie-breaker.
5. test_ma_parse::test_caselaw_year_filter and test_sk_fixes::test_note_says_not_date_sorted: for ma, change the year filter handling in src/world_legal_mcp/jurisdictions/ma.py (near caselaw_filters at :260) so it raises KeyError instead of BadRequest; the `pytest.raises(Exception)` should wrongly stay green. For sk, change the note text at src/world_legal_mcp/jurisdictions/sk.py:393 (pin test).

#### tests_live: Cross-file notes

- Duplicated by test_conformance.py: the per-jurisdiction "search returns hits", "decision round-trip by id", "legislation text/TOC/provision happy path" tests repeat what test_conformance does from each adapter's `samples` (e.g. src/world_legal_mcp/jurisdictions/cz.py:660, pl.py:467, si.py:299, sk.py:310, tr.py:598). Where a jurisdiction file only runs one query and checks one id, it adds nothing. Keep only country-specific behaviour (filters, label variants, bad-input messages), as docs/ADAPTER_SPEC.md:114 asks (2-4 checks).
- Pinned source wording likely to drift: exact headings, dates and case names in assertions (test_ad.py:9, test_al.py:37, test_bb.py:8/16, test_bd.py:40, test_ba.py:55). Counts and "runs to 2022" style claims (test_mm.py:54 `test_mm_law_reports_run_to_2022`) break when the source adds data, not when code breaks. Also pinned error text copied from adapter messages (test_ba.py:22 "must be AP or U", test_bs.py:12, test_ccj.py:15, test_ecowas.py:13, test_efta.py:14, test_icsid.py:15): these test the adapter's own wording, so they pass or fail on a string edit; assert on `BadRequest`/"Bad request" prefix instead (79 tests already use that prefix).
- Weak `or` asserts that stay green on either branch: test_ba.py:55 (`"Ovim zakonom" in out or "Ovim Zakonom" in out` is really a case-insensitive check; lower() it), test_hk.py:29 (`'provision "sch2"' in out or '"sch2"' in out`: the second alternative implies the first, so the first is dead), test_ccj.py:23 (`"Myrie" in summary or "MYRIE"`).
- Only 8 files use `permitted_codes()` for gating; the rest rely on conformance gating. Gating logic is repeated per file: test_bh.py:10-16 and similar. A shared marker in conftest.py would remove it.
- Comments that narrate history ("used to", "now fixed", bug-fix stories) appear in many per-jurisdiction docstrings; these belong in commit messages.

#### tests_live: Deletion candidates

- tests/live/test_conformance.py:119 `test_zz_print_rate_limits`: asserts nothing; its only job is printing. Should be deleted (or run as a script). `grep -rn rate_limit_report src tests` shows the only reader is `_http.py` and this test.
- `pytestmark = pytest.mark.asyncio` in 6 live files (redundant under asyncio_mode = "auto", pyproject.toml:69-71).
- Per-jurisdiction happy-path search/get tests that only repeat the `samples` flow in test_conformance.py (fix is deletion, keep the country-specific ones).
- Offline pure-function tests in the live tree (test_mm.py:11, test_et.py:11): move, not delete.
- test_mm.py:54 `test_mm_law_reports_run_to_2022` and similar "data extent" tests: pin the source's content, not our code; should be deleted.

#### tests_live: Not functional

- tests/live/test_conformance.py::test_zz_print_rate_limits: asserts nothing, stays green however the code behaves.
- tests/live/test_hk.py::(sch2 provision test, line 29): the `or` makes the assert pass when the first form is absent but the looser form is present; the first alternative adds nothing.
- tests/live/test_ba.py::(line 55 test): `or` of two case spellings, so it stays green if the real text changes case; weak but not vacuous.
- tests/live/test_conformance.py::test_search_caselaw / test_get_decision / test_search_legislation / test_toc_and_provision: skip when an adapter has no `samples` entry or the source is in `blocked_sources`, so an adapter can lose coverage silently (skip is not a failure); `fr` skips without PISTE credentials (src/world_legal_mcp/jurisdictions/fr.py:46-47), and az, bh, difc, sg, in, co, gr, de skip when not permitted.
- Tests that assert only `len(out) > 0` or a non-empty string: a source error page or an adapter error message also satisfies them; check per file before trusting.
