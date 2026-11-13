# Validation of ChatGPT's round-2 source research (batch A) — 2026-11-07

Every claim in `research/chatgpt/r2_a.md` was treated as a lead and checked live. Fetches used the repo
client (`world_legal_mcp._http`, UA `Fontes/<ver> (+https://github.com/ykarapazar/fontes)`), a handful of
requests per site, ≥1.2 s apart. No logins, no sign-ups, no header/UA changes, no bot-check bypass, no
contact with anyone. Statements marked "legal background" are from my own knowledge, not fetched.

Two Singapore checks were **not run**: a query
against the eGazette's Algolia search API (using the public search-only key embedded in the page) and a
fetch of a 2026 asset PDF. The eGazette search route is therefore **UNVERIFIED** and an open question.

---

## 1. in — Supreme Court of India judgments (AWS Open Data) — **GO-WITH-CAVEAT (unofficial)**

- **Reachable:** yes. Registry https://registry.opendata.aws/indian-supreme-court-judgments/ — "License CC-BY-4.0", "AWS CLI Access (No AWS account required)", "Update Frequency Bi-monthly"; description says 1950–2025, sourced from eCourts.
- **Search/listing:** no full-text search. Anonymous S3 ListObjectsV2 works:
  `GET https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/?list-type=2&prefix=data/pdf/year=2025/english/&max-keys=3` → 200 XML, keys like `2025_10_131_151_EN.pdf`. With `delimiter=/` year prefixes run 1950–**2026** (2026: 245 English PDFs). Per-file metadata JSON exists (`metadata/json/year=2025/2025_10_131_151.json`); parquet metadata carries title, petitioner, respondent, citation, decision_date.
- **Document:** `data/pdf/year=2025/english/2025_10_131_151_EN.pdf` — 21 pages, text layer: "[2025] 10 S.C.R. 131 : 2025 INSC 1113 Mamman Khan v. State of Haryana (Criminal Appeal No. 4002 of 2025) 12 September 2025". Old material is OCR with errors: `1955_1_1004_1011_EN.pdf` reads "SAKHA WAT ALI ti. THE STATE OF ORISSA", "[1955J".
- **Terms/robots:** dataset CC-BY-4.0; README: "individual PDF and JSON objects are also exposed for targeted access", "Be responsible…". Bucket robots.txt → 404 NoSuchKey. **Upstream** eCourts copyright policy (https://judgments.ecourts.gov.in/pdfsearch/?p=pdf_search/footerlinks/cp&escr_flag=): "The contents on this website shall not be reproduced partially or fully, without duly & prominently acknowledging the source. The contents of this website cannot be used in any misleading or objectionable context or derogatory manner." eCourts robots.txt → 404.
- **Coverage:** ~35K English judgments — these are **SCR reported judgments** (with SCR headnotes), not every SC order. 1950–2026.
- **Caveat:** unofficial mirror; must attribute eCourts prominently; lookup only by year/citation/metadata, so needs a local metadata index for search; old OCR is noisy.
- **ChatGPT errors:** (a) missed the upstream eCourts copyright/attribution policy; (b) presented "35,000 judgments" as SC coverage without noting it is SCR-reported only; (c) repeated the registry's 1950–2025 range — 2026 is present.

## 2. in — Indian High Court judgments (AWS Open Data) — **GO-WITH-CAVEAT (unofficial)**

- **Reachable:** yes. Registry: "25 high courts", CC-BY-4.0, "Update Frequency Quarterly"; the bucket's `dataset.md` says "Update cadence: Daily", "~17.8M judgments", "25 high courts (45 benches)".
- **Search/listing:** no search. Listing by `data/pdf/year=YYYY/court=…/bench=…/` prefix; per-file metadata JSON. `dataset.md`: "downloading millions of individual files is slow… Prefer aws s3 sync on data/tar/".
- **Document:** `year=2025/court=10_8/bench=patnahcucisdb94/BRHC010000012025_1_2025-02-05.pdf` — 2 pages, text: "IN THE HIGH COURT OF JUDICATURE AT PATNA CRIMINAL MISCELLANEOUS No.2062 of 2025".
- **Terms/robots:** CC-BY-4.0; robots 404; same upstream eCourts attribution policy as §1.
- **Coverage:** 1950–2026 partitions. **The `year=` partition is not the decision year:** `year=1995` contains `BRHC010004551983_1_2015-11-03.pdf` (First Appeal No. 401 of 1983, decided 2015). `dataset.md`: "Most records are downloaded from… judgments.ecourts.gov.in, and some courts are backfilled from the eCourts mobile API".
- **Caveat:** unofficial; partly sourced from a mobile API (provenance weaker); quarterly vs daily cadence contradiction; date filtering must use metadata, not prefixes; per-file fetch only for targeted lookups.
- **ChatGPT errors:** (d) missed that year partition ≠ decision year; (e) missed the mobile-API backfill provenance and the eCourts upstream policy.

## 3. sg — Singapore eGazette — **GO-WITH-CAVEAT (official; search UNVERIFIED)**

- **Reachable:** yes. Robots https://www.egazette.gov.sg/robots.txt: "User-Agent: * / Allow: / / Disallow: /search" + Sitemap. https://assets.egazette.gov.sg/robots.txt → 403 AccessDenied.
- **Search/listing:** `/gazettes/` embeds only ~881 items dated 2026-10-13 → 2026-11-06 (≈3.5 weeks), each with `referenceLinkHref`, e.g. `/2026/Legislative Supplements/Acts Supplement/26acts25.pdf` "Finance (Income Taxes) Act 2026". Sitemap: 7 pages; RSS at `/gazettes/rss.xml`. Archive search (`/egazette-browse/`) is client-side **Algolia** (appId 1V7DZGZJKK, index `prod_ogp_egazettes_index`, public search-only key in page). **Not tested — blocked by permission classifier.** `/search` is robots-disallowed.
- **Document:** https://assets.egazette.gov.sg/2025/Legislative%20Supplements/Acts%20Supplement/03.pdf → 200, 26 pages, text: "REPUBLIC OF SINGAPORE GOVERNMENT GAZETTE ACTS SUPPLEMENT Published by Authority NO. 3] FRIDAY, FEBRUARY 14 [2025 … No. 5 of 2025… Electronic Gazette and Legislation Bill". Filename patterns differ by year (`03.pdf` vs `26acts25.pdf`), so URLs are not constructible.
- **Terms** (https://www.egazette.gov.sg/terms-of-use/, "Last updated on 10 July 2026"):
  - General: "Except as set out in clause (11) of these Terms of Use, the Contents shall not be reproduced, republished, uploaded, posted, transmitted or otherwise distributed in any way, without the prior written permission of MDDI."
  - Clause 11 "Reproduction of legislation-Gazettes": "The Government has granted permission to the users of the Website to reproduce any e-Gazettes in any print or electronic material or platform… subject to… conditions" (credit Singapore Government copyright / reproduced with permission; point users to the Website for latest; producer responsible for accuracy; no implied affiliation).
  - **Automated-extraction clause (exact):** "in the case where the producers, or the producers' affiliates or agents, intend to extract the e-Gazettes from the Website through automated means, such extraction of the e-Gazettes from the Website is subject to these Terms of Use and the following conditions: the extraction must not be carried out in an abusive or intrusive, or a deceptive, manner; the extraction must not disrupt or affect the Website's performance, cause any harm or damage to the Website, or breach or circumvent of the Websites security measures."
  - Revocable: "The Government may, at any time and without ascribing any reason or giving any prior notice, revoke the permission…"
  - Also: "Except as set out below, caching and links to, and the framing of, the Website (or any part of it) or any of the Contents are prohibited." Hyperlinks only if "the entire page of the Website (with the Website's banner and logo) must be displayed as it is" — deep links straight to PDFs are questionable. "section 48 of the Interpretation Act (Cap. 1) does not apply to anything printed, downloaded or copied from the Website" (not authoritative copies).
- **Coverage:** FAQ: "All gazettes from Sep 1998 till current date are now available on this website".
- **Caveat:** automation permitted for e-Gazettes with mandatory notices; revocable; caching ban (no local cache beyond the reproduction permission); link-to-landing-page not PDF; archive discovery depends on Algolia — open question whether calling Algolia directly is acceptable. Without it, only the recent ~3.5-week window + RSS is reachable.
- **ChatGPT errors:** (f) missed the caching prohibition and full-page linking condition, and called the permission "explicit" without flagging revocability; (g) implied the catalogue gives a substantial archive — it is a ~3.5-week window; search is Algolia, not a page protocol.

## 4. ar — JUBA (Suprema Corte de Justicia de Buenos Aires) — **GO-WITH-CAVEAT (official, provincial)**

- **Reachable:** yes. https://juba.scba.gov.ar/robots.txt → 404; www.scba.gov.ar robots "User-agent: * Allow: /".
- **Search:** ASP.NET form. `GET Buscar.aspx`, then `POST Buscar.aspx` with all hidden fields (`__VIEWSTATE`, `__EVENTVALIDATION`, `__PREVIOUSPAGE`…) + `ctl00$cphMainContent$txtExpresionBusquedaRapida=contrato`, `ctl00$cphMainContent$ddlMateria=Civil y Comercial`, `ctl00$cphMainContent$btnUnicaBusqueda` → 200, 466 KB: "contrato en Texto del Sumario (6524) en voces (1206) en Texto del Fallo (16793)", 12 `VerTextoCompleto` links (e.g. idFallo=197826). Help PDF: results cap "NO SUPERA LAS 500 ocurrencias".
- **Document:** https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=143376 — HTML: "Causa: B 66927 Fecha: 31/5/2017 … Carátula Pública: Tonelli, Santiago Félix c/ Provincia de Buenos Aires … A C U E R D O En la ciudad de La Plata, a 31 de mayo de 2017". Entities are double-encoded (needs a second unescape).
- **Terms:** none found (JUBA site, help PDF `/descargas/ayudajuba.pdf`, SCBA portal). No explicit licence.
- **Coverage (verified tooltip):** "Incluye Sumarios … de la Suprema Corte de Justicia, a partir del año 1984. Selección de … Cámaras de Apelaciones a partir del año 1990. Fallos in extenso de la SCBA en materia civil y comercial desde el año 1986, y de las restantes materias desde el año 1996."
- **Caveat:** provincial (Buenos Aires) only, not national; no terms either way; stateful ViewState POST is brittle; 500-hit cap.
- **ChatGPT errors:** none found.

## 5. hu — Magyar Közlöny (official gazette) — **GO-WITH-CAVEAT (official)**

- **Reachable:** yes. Robots: "User-agent: * / Disallow:" (empty = allow all).
- **Search:** issue lookup `GET https://magyarkozlony.hu/?year=2026&month=11&serial=167` → "Magyar Közlöny 2026. évi 167. szám 2026. november 6.". **Keyword search works:** `GET https://magyarkozlony.hu/?content=%C3%A9rt%C3%A9kpap%C3%ADr&year=2026` → 200 with snippets ("Magyar Közlöny 2026. évi 164. szám … értékpapír …"). Results are issue-level and mix in Hivatalos Értesítő / Indokolások Tára — filter needed.
- **Document:** `/hivatalos-lapok/msO7X7i2AtmIsrv4xnoA6ae8eacb94e5c/dokumentumok/0a8ebe91d6dcba9c1a6242fb243adc9629c08168/letoltes` — 154 pages, text: "MAGYAR KÖZLÖNY 167. szám … 413/2026. (XI. 6.) Korm. rendelet A magyar állampolgárságról szóló 1993. évi LV. törvény…". 1999 issue 1 (24 pages) has broken ő/ű: "a távh´ ´oszolgáltatásról szóló 1998. évi XVIII. törvény".
- **Terms:** none on reuse/automation. Imprint: publisher Miniszterelnökség, operator MKIFK Zrt.; "Jogszabályi háttér" cites Act CXXX of 2010 and IM rendelet 5/2019. Legal background: Szjt. (Act LXXVI of 1999) §1(4) excludes legislation from copyright.
- **Coverage:** gazette issues (whole-issue PDFs, 1990s–present), not consolidated law.
- **Caveat:** issue-level PDFs (large; need splitting to individual acts); old PDFs need glyph repair; no explicit licence (relies on statutory exclusion).
- **ChatGPT errors:** (h) left keyword search as "not tested" — it works; (i) missed the old-PDF diacritic damage.

## 6. jp — IP High Court (知的財産高等裁判所) — **GO-WITH-CAVEAT (official; tiny subset — national route is better)**

- **Reachable:** yes. Index https://www.courts.go.jp/ip/hanrei/g_panel/index.html — 60 PDF links; "現在係属中の事件はありません".
- **Search:** none for the grand-panel list (static index). National search https://www.courts.go.jp/hanrei/search1/index.html → redirects to `/error_document/sorry.html` (maintenance).
- **Document:** https://www.courts.go.jp/ip/vc-files/ip/2025/hanketsuzenbun-r5ne10040.pdf — 50 pages, text: "令和７年３月１９日判決言渡 令和５年（ネ）第１００４０号 損害賠償請求控訴事件". Margin line numbers interleaved, characters spaced — cleanup needed.
- **National route by id:** https://www.courts.go.jp/assets/hanrei/hanrei-pdf-89254.pdf → 34-page text PDF ("令和２年２月２０日判決言渡 平成３１年(ネ)第１００３３号…"); `/hanrei/89254/detail2/index.html` → 200. IDs are numeric.
- **Terms/robots:** robots only touches `/ip/tetuduki/kozisotatu/index.html` and `/about/sonota/kensin/giketsunoyoushi/index.html` — nothing on `/hanrei`, `/assets`, `/ip/vc-files`. Policy https://www.courts.go.jp/outline/index.html: "当サイトの内容は，写真・イラスト及び無断転載を禁じる旨の注記がある記事を除き，著作権法上認められている利用を行うことができます。 また，当サイトの内容について，裁判所に無断で改変を行うことはできません。" Links "原則として自由" (no implied special relationship; say it is the courts site). Legal background: Copyright Act art. 13 excludes judgments.
- **Caveat:** the grand-panel list is a few dozen cases — not worth its own adapter; extend the existing `jp` adapter to the national `/assets/hanrei/hanrei-pdf-{id}.pdf` + `/hanrei/{id}/detail2/` route instead (no search while search1 is down; id-based fetch only). Don't alter text ("無断で改変") beyond extraction cleanup — keep raw.
- **ChatGPT errors:** (j) "filenames are not uniformly predictable / no national route" — true only for `vc-files`; national id-based URLs work.

## 7. it — Corte costituzionale (decisions + open data) — **GO (official)**

- **Reachable:** yes. https://www.cortecostituzionale.it/robots.txt → 404 (HTML page); dati.cortecostituzionale.it robots → 200 empty.
- **Search:** `/elenco-pronunce` → 200, latest 10 decisions (2026/191…), **no Radware/CAPTCHA**. Form at `/ricerca-pronunce` (formPronuncia → POST `/elenco-pronunce`): `POST https://www.cortecostituzionale.it/elenco-pronunce` body `operazione=ricerca&idTab=tab1&testo=prescrizione&anno=2025` → 10 results (2025/154, 160, 177…); control `testo=zzqxqv` → 0.
- **Document:** https://www.cortecostituzionale.it/scheda-pronuncia/2026/183 — full HTML: "SENTENZA N. 183 ANNO 2026 REPUBBLICA ITALIANA IN NOME DEL POPOLO ITALIANO LA CORTE COSTITUZIONALE composta da: Presidente: Giovanni AMOROSO…".
- **Terms:** data portal: "I dati disponibili in vari formati sono rilasciati con licenza Creative Commons (CC BY SA 3.0) per il libero riuso." No note-legali page on the main site. Legal background: L. 633/1941 art. 5 excludes official acts.
- **Coverage:** "circa 18.000 testi delle pronunce … dal 1956 ad oggi". Portal says both "aggiornati giornalmente" and "cadenza settimanale". Bulk zips (e.g. `CC_OpenPronunce_2001_oggi.zip`) exceed the client's 50 MB cap — bulk only. `/sparql/snorql` → 404.
- **Note:** CC BY-SA 3.0 is ShareAlike for the dataset; site HTML fetched per decision has no licence statement but is an official act. Fills Italy's case-law gap.
- **ChatGPT errors:** (k) claimed Radware CAPTCHA on `/elenco-pronunce` — not reproduced; (l) "no usable search" — the POST search works.

---

## Other countries (one line each)

- **Ireland — NO:** https://judgments.courts.ie/robots.txt = "User-agent: * / Disallow: /" (confirmed); ChatGPT's "none found" agrees. BAILII/IRLII not rechecked.
- **Israel (VERSA, Yeshiva Univ.) — NO without written permission:** VERSA robots has Crawl-delay 10, but its terms point to Yeshiva University's (https://www.yu.edu/website-terms-use): "solely for your personal, noncommercial home use… Except as expressly authorized in advance by us in writing" and prohibits "spidering," "screen scraping," "database scraping". Selective English translations only. ChatGPT left this unresolved and missed the explicit scraping ban.
- **Denmark (Domsdatabasen) — NEEDS-PERMISSION:** "Der skal ansøges om API-adgang til Domsdatabasen… Det vil dog være et krav, at ansøgeren har et anerkendelsesværdigt formål." Matches `dk.py` note.
- **China (SPC Civil Code page 233181) — NO (too narrow):** reachable, full text through "第一千二百六十条 本法自2021年1月1日起施行", footer "中华人民共和国最高人民法院 版权所有"; one statute only; flk.npc robots excludes automation.
- **Norway (Lovdata) — NO:** §2.3 NLOD 2.0 grant verified ("fritt kopiere, bruke og dele… Massenedlasting og systematiske uttrekk er ikke tillatt. For større nedlastinger, bruk våre åpne API-er"), but robots ends "User-agent: * / Disallow: /". ChatGPT correct.
- **Australia (AustLII) — NO (blocked):** robots "Content-Signal: search=yes,ai-train=no,use=reference / Allow: /" + EU DSM Art. 4 reservation, but `/austlii/copyright.html` and `/au/cases/cth/HCA/2024/1.html` → 403 for our UA.
- **Australia (JADE) — NO:** https://jade.io/terms licence is "for the purpose of your own research or study and for the provision of professional legal advice and services to your clients"; robots disallows `/search*`, `/j/*`, `/*.do`, `/citation*`.

---

## Summary

| Source | Verdict | One-line reason |
|---|---|---|
| in — SC judgments (AWS) | GO-WITH-CAVEAT (unofficial) | CC-BY-4.0, anonymous S3 per-file access; SCR-reported only; must credit eCourts; no search |
| in — High Court judgments (AWS) | GO-WITH-CAVEAT (unofficial) | CC-BY-4.0, 17.8M files; year prefix ≠ decision year; partial mobile-API provenance; no search |
| sg — eGazette | GO-WITH-CAVEAT (official) | Clause 11 permits automated extraction with notices; revocable; caching ban; archive search (Algolia) UNVERIFIED — open question |
| ar — JUBA (SCBA) | GO-WITH-CAVEAT (official, provincial) | Search + full text work; no terms either way; Buenos Aires province only |
| hu — Magyar Közlöny | GO-WITH-CAVEAT (official) | Robots allow all; keyword + issue search work; issue-level PDFs, old glyph damage |
| jp — IP High Court | GO-WITH-CAVEAT (official) | Tiny list; better: extend `jp` to national `/assets/hanrei/hanrei-pdf-{id}.pdf` |
| it — Corte costituzionale | GO (official) | No CAPTCHA, POST search works, CC BY-SA 3.0 open data, 1956– |
| ie | NO | judgments.courts.ie robots Disallow / |
| il — VERSA | NO (w/o written permission) | YU terms: personal noncommercial use, scraping banned |
| dk — Domsdatabasen | NEEDS-PERMISSION | API access by application |
| cn — SPC Civil Code page | NO | single statute; flk.npc robots-excluded |
| no — Lovdata | NO | robots Disallow / |
| au — AustLII | NO | 403 for our UA |
| au — JADE | NO | research/advice-only licence; robots disallows content paths |

**ChatGPT errors found: 13.**

1. India SC: missed the upstream eCourts copyright/attribution policy.
2. India SC: "35,000 judgments" presented as SC coverage — it is SCR-reported judgments only.
3. India SC: 1950–2025 range is stale; 2026 present.
4. India HC: missed that the `year=` partition is not the decision year.
5. India HC: missed mobile-API backfill provenance and the eCourts policy.
6. Singapore: missed the caching prohibition and the full-page (no deep-link-to-PDF) linking condition.
7. Singapore: called the permission "explicit" without flagging that it is revocable at any time.
8. Singapore: implied the catalogue yields an archive — it is a ~3.5-week window; archive search is Algolia.
9. Hungary: keyword search left as untested — it works.
10. Hungary: missed diacritic damage in old PDFs.
11. Japan: "no predictable national route" — national id-based PDF and detail URLs work.
12. Italy: Radware CAPTCHA on `/elenco-pronunce` — not reproduced (200, list returned).
13. Italy: "no usable search" — POST `/elenco-pronunce` search works with a 0-hit control.

Not counted: Israel VERSA left as "unresolved" rather than wrong (but the YU scraping ban was missed); Italy's daily-vs-weekly cadence contradiction is the portal's own.
