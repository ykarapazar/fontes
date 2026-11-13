# CEE, Balkans, Turkey & CIS: legal data sources for world-legal-mcp

Research date 2026-11-05. Probes were run from a **UK IP (GB)** with a Chrome User-Agent, using read-only GET/POST searches, a handful per source.
- "verified" means I got a real payload back on 2026-11-05.
- "reachable" means the site answered with HTTP 200 but I did not test a search or document call.
- "timeout (UK)" means the TCP connection never completed from the UK. That is probably geo or IP filtering, but I did not confirm it from another country.
- Anything else is marked **unverified**.

Tiers: **A** = official API, no key · **B** = official API, free key · **C** = HTML only (or an undocumented SPA JSON backend), automated access tolerated · **D** = paid, forbidden, nothing usable, or geo-blocked.

> Rule of thumb in this region: most "APIs" are **undocumented JSON backends of SPAs**
> (Turkey Bedesten, Anayasa KBB, Czech sbr-cache, Slovenia PIS/sodnapraksa). They are keyless and
> fast but have no SLA or published terms. Officially documented open APIs exist only in PL (Sejm ELI,
> SAOS), CZ (e-Sbírka SPARQL, rozhodnuti.justice.cz opendata), RO (SOAP), and RU (publication.pravo.gov.ru).

## Summary table

| Jurisdiction | Case law tier | Legislation tier | Best endpoint | Auth | Notes |
|---|---|---|---|---|---|
| **Turkey** | **A/C** (Bedesten JSON, AYM JSON) | **A/C** (Bedesten mevzuat JSON) | `POST bedesten.adalet.gov.tr/emsal-karar/searchDocuments` + `/mevzuat/searchDocuments` | none | Verified. One backend serves Yargıtay, Danıştay, BAM/istinaf, local courts and all legislation, with full-text search. **yargi-mcp is now commercial (Yargı PRO) and its repo was wiped on 2026-10-28. The mevzuat-mcp repo is 404.** |
| **Poland** | A (SAOS) / C (NSA, SN, TK) | **A** (Sejm ELI API) | `api.sejm.gov.pl/eli/...`, `saos.org.pl/api/search/judgments` | none | Verified. Catch: SAOS data for SN, TK and KIO is **frozen around 2015–2018**. Only common courts are current. The common-courts portal sits behind an F5 bot challenge. NSA robots.txt disallows `/cbo/find`. |
| **Czechia** | **A** (rozhodnuti.justice.cz opendata) / C (NS, NSS, ÚS) | **A** (e-Sbírka SPARQL + sbr-cache JSON) | `e-sbirka.gov.cz/sbr-cache/...`, `rozhodnuti.justice.cz/api/opendata` | none | Verified. Best-structured legislation in the region: per-fragment, consolidated by date, ELI. |
| **Ukraine** | C (reyestr HTML + CC-BY yearly dumps) | **D from UK** (zakon.rada.gov.ua times out) | `POST reyestr.court.gov.ua/` (form) | none (captcha CSS present) | Case-law full-text search verified (1.14M hits for one query). The legislation host is unreachable from the UK, so it needs a proxy in UA/EU. |
| **Romania** | D/C (ReJust and ICCJ HTML; portalquery SOAP has case metadata only) | **A in principle; broken today** | `http://legislatie.just.ro/apiws/FreeWebService.svc/SOAP` | token via `GetToken` (no registration) | GetToken works. `Search` returns a fault (backend Solr refused). The HTTPS site returns an empty reply from the UK. |
| Slovakia | C (obcan.justice.sk, nsud.sk) | A/C (static.slov-lex.sk HTML mirror) | `static.slov-lex.sk/static/SK/ZZ/{yyyy}/{n}/` | none | Static mirror verified. |
| Hungary | C (eakta.birosag.hu BHGY) | C (njt.jog.gov.hu, ELI redirect) | `njt.jog.gov.hu/eli/TV/2013/5` | none | `njt.hu` times out from the UK, but `njt.jog.gov.hu` works. robots.txt disallows `/or/*` and `/justification_search/*`. |
| Slovenia | C (sodnapraksa.si SPA backend) | C (pisrs.si SPA, `pisrs.si/api`) | `pisrs.si/api/...` | none (sodnapraksa has Keycloak for some features) | Both are new SPAs. Backends are discoverable but undocumented. sodnapraksa has a semantic search mode. |
| Croatia | **D** (odluke.sudovi.hr: robots `Disallow: /`) | C (narodne-novine.nn.hr ELI) | `narodne-novine.nn.hr/eli/sluzbeni/{y}/{issue}/{n}` | none | The NN ELI → HTML redirect is verified. The court portal forbids crawling. |
| Bulgaria | D (legalacts.justice.bg, vks.bg time out from UK) | C (dv.parliament.bg JSF; lex.bg private) | – | – | Poor. |
| Serbia | C/D (vrh.sud.rs HTML) | C (pravno-informacioni-sistem.rs, free state PIS) | – | – | Reachable only. Paragraf.rs is commercial. |
| Bosnia & H. | D (CSD/pravosudje.ba: registration and paid) | D/C (official gazettes, paid) | ustavnisud.ba (Constitutional Court HTML) | – | Reachable only. |
| North Macedonia | D (sud.mk times out) | D (slvesnik.com.mk is paid) | – | – | – |
| Albania | C (gjykataelarte.gov.al) | C (qbz.gov.al Angular SPA) | – | – | Reachable only. |
| Montenegro | D (sudovi.me 403 from UK) | C (sluzbenilist.me) | – | – | – |
| Kosovo | D (gjyqesori-rks.org 403) | C (gzk.rks-gov.net) | – | – | – |
| Moldova | C (instante.justice.md) | D from UK (legis.md 403 WAF) | – | – | – |
| Georgia | C (supremecourt.ge, ecd.court.ge) | C (matsne.gov.ge, good HTML + EN translations) | `matsne.gov.ge/{ka,en}/document/view/{id}` | none | Reachable and large HTML. Search is HTML. |
| Armenia | C (court.am; datalex.am times out) | C (arlis.am) | – | – | Reachable only. |
| Azerbaijan | D (supremecourt.gov.az, courts.gov.az time out) | C (e-qanun.az, Next.js) | `e-qanun.az/framework/{id}` | none | – |
| Kazakhstan | D (office.sud.kz times out) / C (sud.gov.kz) | C (adilet.zan.kz SPA) | – | – | – |
| Russia | C/D (sudact.ru is private, results loaded by JS; kad.arbitr.ru has anti-bot; vsrf.ru and bsr.sudrf.ru time out) | **A** (publication.pravo.gov.ru JSON API, official publication only) | `publication.pravo.gov.ru/api/Documents` | none | The API is verified, but it covers publication, **not consolidated text** (consolidated text is on pravo.gov.ru IPS, which times out from the UK). |

## Existing OSS to know about (cross-cutting)

- **MateMatic Solutions** (`github.com/matematicsolutions`, Apache-2.0 / MIT, very active Sep–Nov 2026) builds one connector per country under a shared "citation contract". Connectors in this region:
  - **Poland:** `mcp-isap`, `mcp-saos`, `mcp-nsa`, `mcp-krs`, `mcp-eureka`, `kio-orzeczenia-mcp`, `uodo-orzeczenia-mcp`, and the umbrella `prawo-pl-mcp` (5 tools wrapping all of these).
  - **Other countries:** `cz-eli-mcp` (SPARQL), `sk-eli-mcp` (static.slov-lex), `hu-eli-mcp` (njt.jog.gov.hu ELI, honours robots), `hr-eli-mcp` (Narodne novine), `ro-eli-mcp` (SOAP), `tr-eli-mcp` (Bedesten mevzuat).
  - These are the closest prior art to world-legal-mcp, and a ready source of endpoint knowledge. All are low-star (0–8). Their code is useful as reference.
- **saidsurucu/sbirka-mcp** (CZ e-Sbírka REST via sbr-cache, 9★, no licence file, last push 2026-03-02). Same author as yargi-mcp.
- **legalize-dev** ("law-as-git", 32 jurisdictions). In-region: `legalize-pl`, `legalize-cz`, `legalize-sk`, `legalize-ro`, `legalize-ua`. Licence NOASSERTION, MIT for UA. `legalize-ua` is **essentially empty** (2 KB repo, "early stage"). It is a bulk-mirror approach, which goes against the live-fetch design, but it is a possible fallback where the live source is geo-blocked.

---

## Turkey (depth)

### Status of saidsurucu's packages (critical)

| | yargi-mcp | mevzuat-mcp |
|---|---|---|
| GitHub | `github.com/saidsurucu/yargi-mcp`: **repo wiped 2026-10-28**. It is now a 1-commit repo, created 2026-10-28, containing only a README: "Yargı MCP → Yargı PRO: proje taşındı". The free hosted endpoint `yargimcp.surucu.dev` is shut down. The paid successor is `https://app.yargipro.com/mcp` (14-day trial), which covers ~11M decisions, AYM, 12 legislation types, Resmî Gazete, and 18 regulators. | `github.com/saidsurucu/mevzuat-mcp`: **HTTP 404** (deleted or private). The PyPI project URLs still point to it. |
| PyPI | 0.2.2 (2026-07-14), **MIT** (LICENSE in sdist: "Copyright (c) 2025 saidsurucu"). Still downloadable. | 0.3.0 (2025-10-10), **MIT**. Still downloadable. No release for over a year. |
| Heavy deps | fastmcp, httpx, aiohttp, markitdown[pdf], pypdf, openai, numpy, cryptography (semantic search via OpenRouter embeddings; optional) | **playwright 1.55 (installs Chromium in setup.py)**, mistralai (OCR of PDFs, needs `MISTRAL_API_KEY`), markitdown 0.1.3 pinned |
| Community forks/clones | `ShaironYT59/yargi-mcp` (20★, MIT, non-fork copy, pushed 2026-10-13), `MCYBA/yargi-mcp`, `Remilya/yargi-mcp` | – |

**Implication:** the MIT code in the PyPI 0.2.2 / 0.3.0 sdists can legally be vendored or forked (keep the copyright notice). Do not *depend* on these packages, because upstream is gone and the author's incentive is now the paid product. **Recommendation: reimplement.** The endpoints are simple JSON POSTs, verified below. Use the 0.2.2 sdist as a reference for headers, rate limits, and HTML→markdown quirks. A reimplementation also drops Playwright, Mistral, and OpenAI.

Other Turkish MCPs:
- `aydincan/turk-hukuku-ictihat-mcp` (MIT, 21★): case law via emsal.uyap, Danıştay, AYM, mevzuat.adalet.
- `aydincan/turk-hukuku-mevzuat-mcp` (MIT, 7★): legislation via mevzuat.gov.tr.
- `matematicsolutions/tr-eli-mcp` (Apache-2.0): legislation via the Bedesten mevzuat API. Its notes say the Yargıtay site is unreachable from its build network.
- `afsozer/dayanak` (AGPL-3.0, formerly emsal-mcp): citation-verified research.

### What yargi-mcp 0.2.2 covered and how (from the sdist source)

| Module | Source | Method |
|---|---|---|
| bedesten | `bedesten.adalet.gov.tr/emsal-karar/{searchDocuments,getDocumentContent}` | JSON POST. itemType `YARGITAYKARARI`, `DANISTAYKARAR`, `YERELHUKUK`, `ISTINAFHUKUK`, `KYB` (kanun yararına bozma). Chamber filter `birimAdi`. Dates `kararTarihiStart/End`. |
| yargitay | `karararama.yargitay.gov.tr/aramalist` | JSON POST (legacy). **Timeout from UK** |
| danistay | `karararama.danistay.gov.tr` | JSON (keyword + detailed) |
| emsal | `emsal.uyap.gov.tr/aramadetaylist`, `/getDokuman?id=` | JSON POST, HTML doc |
| anayasa | `{kararlarbilgibankasi,normkararlarbilgibankasi}.anayasa.gov.tr/api/core/public/search` | JSON POST. `kararTipi` = `BireyselBasvuru` / `NormDenetimi`. Old `/Ara`, `/ND`, `/BB` HTML paths now 404. |
| uyusmazlik | `kararlar.uyusmazlik.gov.tr` | HTML form |
| kik | `ekapv2.kik.gov.tr` | EKAP v2 (public procurement board) |
| rekabet | `rekabet.gov.tr/tr/Kararlar` | HTML + PDF |
| sayistay | `sayistay.gov.tr` | HTML (genel kurul, temyiz kurulu, daire) |
| kvkk | via **Brave Search API** (`BRAVE_API_KEY`, paid key) site-search on kvkk.gov.tr | not a direct source |
| bddk, sigorta_tahkim | via **Tavily API** (`TAVILY_API_KEY`) | not a direct source |
| btk, gib (özelge) | `btk.gov.tr`, `gib.gov.tr/api` | HTML / JSON |

mevzuat-mcp 0.3.0 scrapes `www.mevzuat.gov.tr/Anasayfa/MevzuatDatatable`, which needs an antiforgery token. It downloads PDFs from `/MevzuatMetin/{tur}.{tertip}.{no}.pdf` and OCRs them with Mistral. It exposes 18 tools: kanun, KHK, tüzük, CBK, CB yönetmelik, CB kararı, CB genelge, kurum yönetmeliği, tebliğ, plus search-within. **The Bedesten mevzuat API below is strictly better**: JSON, an article tree, and per-article content, with no OCR.

### Case law: Bedesten (Ministry of Justice / UYAP Mevzuat backend). Tier A/C

- **Search:** `POST https://bedesten.adalet.gov.tr/emsal-karar/searchDocuments`
  - Headers: `Content-Type: application/json; charset=utf-8`, `AdaletApplicationName: UyapMevzuat`. The Origin/Referer of `mevzuat.adalet.gov.tr` are sent by clients but are not strictly needed.
  - Body: `{"data":{"pageSize":10,"pageNumber":1,"itemTypeList":["YARGITAYKARARI"],"phrase":"\"kira tespiti\"","birimAdi":"3. Hukuk Dairesi","kararTarihiStart":"2025-01-01T00:00:00.000Z","kararTarihiEnd":"...","sortFields":["KARAR_TARIHI"],"sortDirection":"desc"},"applicationName":"UyapMevzuat","paging":true}`
  - Returns `emsalKararList[{documentId, birimAdi, esasNo, kararNo, kararTarihiStr, itemType}]` plus `total`.
  - **Verified 2026-11-05:** "kira tespiti" in Yargıtay → total 2,104, latest decision 17.06.2026. "imar" in Danıştay → 43,511.
- **Document:** `POST /emsal-karar/getDocumentContent` with `{"data":{"documentId":"1231758000"},"applicationName":"UyapMevzuat"}`. Returns `{content: base64, mimeType: text/html | application/pdf}`. Verified.
- **Phrase syntax:** quoted phrases, `+required`, `-exclude`, AND/OR/NOT. No wildcards.
- **Page size:** 1–10 per the yargi-mcp model. Larger sizes are unverified.
- **Rate limit:** yargi-mcp measured **~10 requests / 30 s per IP**, enforced with a 429 + Retry-After. Default spacing is 3.5 s.
- **Terms:** no published API terms. It is an undocumented backend of the public `mevzuat.adalet.gov.tr` site. Decisions are public documents (anonymised).
- **Language:** Turkish.
- **Public link format:** `https://mevzuat.adalet.gov.tr/ictihat/{documentId}`.
- **Yargıtay/Danıştay data lag:** the newest Yargıtay hit was June 2026, about 5 months before the probe date.

**UYAP Emsal (BAM/istinaf and local courts):**
- Search: `POST https://emsal.uyap.gov.tr/aramadetaylist` with `{"data":{"arananKelime":"kira","pageSize":1,"pageNumber":1}}`.
- **Verified:** 49,884 hits; top hit İstanbul BAM 54. HD, 16.09.2026.
- Document: `GET /getDokuman?id=`.

**Anayasa Mahkemesi (KBB):**
- Search: `POST https://kararlarbilgibankasi.anayasa.gov.tr/api/core/public/search` with `{"kararTipi":"BireyselBasvuru","query":"ifade özgürlüğü","page":1,"size":10}`.
- **Verified:** 15,949 individual-application (BB) hits and 2,714 constitutional-review (Norm) hits.
- Full HTML: request `{"kararTipi":..., "id":"<uuid>"}` and read `data[0].icerik`.
- SPA document URL: `/kbb/pages/search/{tipi}?id=base64url("kbb:"+uuid)`.

**Yargıtay's own site** (`karararama.yargitay.gov.tr`): **times out from the UK.** The MateMatic author reported the same from their network. Use Bedesten instead, which carries the same Yargıtay corpus.

**Danıştay** (`karararama.danistay.gov.tr`): reachable (200).

### Legislation: Bedesten mevzuat. Tier A/C

- `POST https://bedesten.adalet.gov.tr/mevzuat/searchDocuments`
  - Body: `{"data":{"pageSize":20,"pageNumber":1,"sortFields":["RESMI_GAZETE_TARIHI"],"sortDirection":"desc","phrase":"...","mevzuatAdi":"...","mevzuatNo":"6098","mevzuatTurList":["KANUN"],"basliktaAra":false,"tamCumle":false},"applicationName":"UyapMevzuat","paging":true}`
  - Setting `basliktaAra:false` gives **full-text search**. Verified: "kişisel verilerin korunması" → 536 hits.
  - `mevzuatNo:6098` + KANUN → TBK, `mevzuatId 103273`. Verified.
- Content: `POST /mevzuat/getDocumentContent` with `{"documentType":"MEVZUAT","id":mevzuatId}` for the whole law, or `{"documentType":"MADDE","id":maddeId}` for **one article**.
- Article tree: `POST /mevzuat/mevzuatMaddeTree` with `{"mevzuatId":...}`.
- Types: `POST /mevzuat/mevzuatTypes`. (Endpoints from tr-eli-mcp; I verified search only.)
- **Consolidated:** yes. It serves the current text, the same text as mevzuat.gov.tr.
- **Identifier:** `MevzuatNo` + `MevzuatTur` (1 = Kanun …) + `MevzuatTertip` (5 = current series). Canonical URL: `https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5`.
- No ELI.
- **mevzuat.gov.tr:** HTML and the PDF `/MevzuatMetin/1.5.6098.pdf` are reachable (verified 200, 848 KB). This is the fallback.
- **Resmî Gazete:** `resmigazete.gov.tr` is reachable, HTML only.

### Turkish sources that saidsurucu's packages miss or handle weakly

- **KVKK:** only reachable through a paid Brave Search key. `kvkk.gov.tr` itself **timed out from the UK**.
- **BDDK and Sigorta Tahkim:** only through a paid Tavily key.
- **Not covered at all:**
  - SPK (Capital Markets Board) bülten decisions
  - EPDK
  - RTÜK
  - Kamu Denetçiliği Kurumu (Ombudsman)
  - Yargıtay İçtihadı Birleştirme as a separate feed (it is in Bedesten via `birimAdi`)
  - Bölge İdare Mahkemeleri (administrative appeal courts; check Bedesten `itemTypeList` values beyond the 5 known ones; unverified)
  - Resmî Gazete daily index
  - TBMM bill and gerekçe texts (`gerekceId` appears in Bedesten mevzuat records; possibly fetchable; unverified)
- **Covered, but by scraping:** Rekabet Kurumu, Sayıştay, KİK (all reachable from the UK, 200).

---

## Poland (depth)

**Legislation: Sejm ELI API. Tier A. Verified.**
- Base: `https://api.sejm.gov.pl/eli`. Documented (Swagger at `api.sejm.gov.pl`). No key.
- Covers Dziennik Ustaw (DU) and Monitor Polski (MP) from 1918 onward, about 96k acts according to the mcp-isap README.
- Search: `GET /eli/acts/search?title=kodeks%20cywilny&limit=3`. Filters: year, type, keyword, `inForce`. Title/metadata search only; **no full-text search** (unverified for text).
- Act: `GET /eli/acts/DU/1964/93`. Verified: "Kodeks cywilny", status "akt posiada tekst jednolity", text types H/O/I/U.
- Text: `/eli/acts/DU/1964/93/text.html` (2.2 MB, verified) and `/text.pdf`.
- Structure: `/eli/acts/DU/1964/93/struct`. This is the **article tree** (part → book → art). Verified, 281 KB.
- ID scheme: `DU/{year}/{pos}`. ELI `/eli/DU/1964/93`.
- **Gotcha:** the act's HTML is the *original* text. The **consolidated text** is a separate act: an Obwieszczenie (announcement) of the uniform text, e.g. `DU/2026/795` for KC. Recent ones are often **PDF-only** (`textHTML:false`). Per-article consolidated text therefore means parsing a PDF, or relying on older consolidated HTML.
- ISAP (`isap.sejm.gov.pl`) is the HTML front end of the same data.

**Case law: SAOS. Tier A. Verified, but stale.**
- `GET https://www.saos.org.pl/api/search/judgments?all=umowa%20najmu&pageSize=..&courtType=..&sortingField=JUDGMENT_DATE&sortingDirection=DESC`. Full-text search, JSON, no key. Single judgment: `/api/judgments/{id}`.
- Licence: CC0 / open data (ICM, University of Warsaw).

Counts on 2026-11-05:

| courtType | Count | Newest judgmentDate |
|---|---|---|
| `COMMON` | 475,072 | current; "umowa najmu" → newest 2026-10-22 |
| `SUPREME` | 38,081 | **2016-06-22** |
| `CONSTITUTIONAL_TRIBUNAL` | 9,503 | **2015-12-09** |
| `NATIONAL_APPEAL_CHAMBER` | 22,168 | **2018-09-06** |
| `ADMINISTRATIVE` | 0 | – |

- **Gotcha:** SAOS is effectively a **common-courts-only feed** today. It also has date junk: one record is dated 3013-12-04, so filter `judgmentDateTo`.

**Other Polish case-law sources:**
- **Common courts portal** `orzeczenia.ms.gov.pl`: returns an **F5/TSPD JavaScript bot challenge** to curl (`window["bobcmn"]`), so it is not usable without a headless browser. SAOS mirrors it.
- **NSA/WSA CBOSA** `orzeczenia.nsa.gov.pl`: HTML. **robots.txt disallows `/cbo/find`, `/cbo/search` and `/doc/*.txt` for all agents, and blocks GPTBot entirely.** MateMatic's `mcp-nsa` scrapes it anyway. Treat as tier C with legal caution, or D if we honour robots.
- **Supreme Court** `sn.pl` (SharePoint search), **TK** `trybunal.gov.pl`, `ipo.trybunal.gov.pl`: HTML, reachable. Not tested further. KIO: `orzeczenia.uzp.gov.pl`. UODO: `orzeczenia.uodo.gov.pl`.

**MCPs:** MateMatic `prawo-pl-mcp` (umbrella, Apache-2.0), `mcp-isap`, `mcp-saos`, `mcp-nsa` (MIT); `barwojcik/legal_mcp` (RAG, offline).

---

## Czechia (depth)

**Legislation: e-Sbírka. Tier A. Verified.**
- **SPARQL (official open data):** `https://opendata.eselpoint.gov.cz/sparql`. Virtuoso; keyless; verified (returns JSON results). ELI URIs look like `https://opendata.eselpoint.gov.cz/esel-esb/eli/cz/sb/2019/110`. Used by MateMatic `cz-eli-mcp`.
- **REST (the SPA's backend):** base `https://e-sbirka.gov.cz/sbr-cache`. The old `www.e-sbirka.cz` returns 308 to e-sbirka.gov.cz, so update any client that hardcodes `.cz`, as `saidsurucu/sbirka-mcp` does.
  - Metadata: `GET /dokumenty-sbirky/{urlencoded staleUrl}`, e.g. `%2Fsb%2F2012%2F89%2F0000-00-00`. Verified: returns the citation, ELI `/eli/cz/sb/2012/89/0000-00-00`, and effective dates.
  - Fragments (per-paragraph tree, consolidated): `GET /dokumenty-sbirky/{id}/fragmenty?cisloStranky=0`. Verified.
  - Full-text search: `POST /jednoducha-vyhledavani` with `{"fulltext":"nájem bytu","start":0,"pocet":25,"razeni":["+relevance"]}`. Verified: 1,686 hits. Facets via `fazetovyFiltr`.
- **Consolidated by date:** yes. The trailing date in `staleUrl` / ELI (`0000-00-00` = current) selects the version.
- Identifier: `{sbirka}/{year}/{number}/{version date}`, e.g. `sb/2012/89`.
- **Terms:** open data (e-Sbírka is a statutory open register). The REST layer is undocumented.

**Case law:**
- **rozhodnuti.justice.cz open data. Tier A. Verified.**
  - Index: `GET /api/opendata` lists years with counts (2021: 150,939 · 2022: 181,861 · 2023: 85,462 · 2024: 61,203 · 2025: 71,515 …).
  - Per day: `GET /api/opendata/{yyyy}/{mm}/{dd}` returns items with jednaciCislo, soud, **ECLI**, predmetRizeni, keywords, cited provisions (`zminenaUstanoveni`), and an `odkaz`.
  - Full text: `GET /api/finaldoc/{uuid}` returns structured JSON paragraphs.
  - Covers district and regional courts (published since 2020/21). There is **no keyword-search API**: only browsing by date. The website has search, but its API is unverified. For live keyword search you need the HTML front end or a local index.
- **Supreme Court (NS):** `sbirka.nsoud.cz` returned **503**. `nsoud.cz` is reachable, but the legacy Lotus Notes `judikatura_ns.nsf/WebSearch` returned 404, so the path has changed (unverified).
- **Supreme Administrative Court (NSS):** `vyhledavac.nssoud.cz`, HTML search, reachable.
- **Constitutional Court (ÚS):** `nalus.usoud.cz/Search/Search.aspx`, ASP.NET HTML, reachable.
- All three are tier C.

**MCPs:** MateMatic `cz-eli-mcp` (Apache-2.0); `saidsurucu/sbirka-mcp` (no licence file, so all rights reserved by default; uses the old `.cz` base). legalize-cz is a bulk mirror.

---

## Ukraine (depth)

**Legislation: `zakon.rada.gov.ua` / `data.rada.gov.ua`. Tier D from the UK.**
- Every request **timed out** from the UK IP: `/laws/show/435-15`, `.txt`, `.json`, `/open/data/`, `/api/token`, `robots.txt`.
- Known (unverified from here): the open-data API needs a free token (`data.rada.gov.ua/api/token`), so it would be tier B where reachable. Formats: `/laws/show/{nreg}.txt|.json`. Identifier is the registration number `nreg`, e.g. `435-15` (Civil Code), `254к/96-вр` (Constitution). The text is consolidated, with an edition history.
- **Needs an egress proxy in Ukraine or the EU, or a mirror.** `legalize-ua` (MIT) claims ~43k acts from data.rada, but the repo is essentially empty today.

**Case law: Unified State Register of Court Decisions (ЄДРСР), `reyestr.court.gov.ua`. Tier C. Verified.**
- Search: `POST https://reyestr.court.gov.ua/` (form fields `SearchExpression`, `CourtRegion`, `INSType`, `CSType`, `RegDateBegin/End`, `CaseNumber`, `PagingInfo.ItemsPerPage`, `Sort`, `Liga`). Send cookies from a GET first.
- Verified: "оренда землі" → "знайдено документів: 1138346", with result links `/Review/{id}`.
- Document: `GET /Review/{id}`. Verified: HTML full text (2024 Kharkiv administrative court decision).
- The page CSS includes captcha styles, so expect a captcha after repeated queries (unverified threshold).
- **Bulk alternative:** data.gov.ua dataset `16ab7f06-7414-405f-8354-0a492475272d`, CKAN API verified. Yearly ZIP `edrsr_data_2026.zip` under **CC-BY**, updated 2026-11-05. That is bulk, not live.
- court.gov.ua is reachable. Language: Ukrainian.

**MCPs:** none found on GitHub.

---

## Romania (depth)

**Legislation: Portal Legislativ (legislatie.just.ro). Tier A in principle, currently broken.**
- SOAP endpoint: `http://legislatie.just.ro/apiws/FreeWebService.svc/SOAP` (WSDL `?wsdl`). Call `GetToken` (no registration), then `Search(SearchModel{NumarPagina, RezultatePagina, SearchAn, SearchNumar, SearchText, SearchTitlu}, tokenKey)`.
- **2026-11-05:** `GetToken` **works** over plain HTTP. `Search` returns a WCF fault: "No connection could be made … 10.1.14.16:8983", meaning the backend Solr is down. Re-test before building.
- The HTTPS website (`/Public/DetaliiDocument/{id}`, `/Public/DetaliiDocumentAfis/{id}` = consolidated "forma consolidată") **returns an empty reply / HTTP2 stream error to the UK IP** with any User-Agent. The certificate is valid, so this is a WAF or geo filter (unverified which). Plain HTTP redirects to HTTPS.
- Identifier: internal numeric document id, e.g. 109884. Consolidated forms exist as separate ids.
- **MCP:** MateMatic `ro-eli-mcp` (Apache-2.0, SOAP).

**Case law:**
- **ReJust** `rejust.ro` (CSM, anonymised decisions of all courts): reachable (200). HTML search; it historically required account login for full features (unverified now). Tier C/D.
- **ICCJ (High Court):** `iccj.ro/cautare/` returned **503**. **Constitutional Court:** `ccr.ro` returned **503**. Both share the same 8,904-byte error page, so a common WAF is likely.
- **portalquery.just.ro:** `query.asmx?WSDL` works (verified, 90 KB WSDL). This is a public SOAP service for **case files and hearings (dosare)** across courts, not decision texts. Useful for metadata.
- `portal.just.ro` returns 403 from the UK. `rolii.ro` and `jurisprudenta.csm1909.ro` time out.

---

## Slovakia
- **Legislation:** Slov-Lex. `www.slov-lex.sk/pravne-predpisy/SK/ZZ/{y}/{n}/` redirects (301) to `redir.slov-lex.sk`.
  - Keyless static mirror: `https://static.slov-lex.sk/static/SK/ZZ/1964/40/` (Civil Code), verified 200. Original text: `.../vyhlasene_znenie.html` (965 KB, verified). Consolidated versions sit under dated sub-paths (unverified pattern).
  - ID: `SK/ZZ/{year}/{number}`. ELI is supported by Slov-Lex (unverified here).
  - MCP: MateMatic `sk-eli-mcp`. Tier A/C.
- **Case law:** `obcan.justice.sk/infosud/-/infosud/zoznam/rozhodnutie` (HTML, 200) and `nsud.sk/rozhodnutia/` (200). A JSON API behind obcan.justice.sk is unverified. Tier C.

## Hungary
- **Legislation:** Nemzeti Jogszabálytár. `njt.hu` **times out from the UK**, but `njt.jog.gov.hu` works.
  - ELI `https://njt.jog.gov.hu/eli/TV/2013/5` redirects (302) to `/jogszabaly/2013-5-00-00` (1.45 MB consolidated HTML, verified).
  - robots.txt allows `/jogszabaly/*` and `/search_kozismert/*`, and disallows `/or/*` and `/justification_search/*`.
  - ID: `{year}-{number}-{type}-{…}`. ELI `/eli/TV/{y}/{n}`. Tier C (ELI resolves; HTML only). MCP: MateMatic `hu-eli-mcp`.
- **Case law:** the Bírósági Határozatok Gyűjteménye at `eakta.birosag.hu/anonimizalt-hatarozatok` (2.2 MB HTML search page, 200). robots.txt returned an error page. The old `birosag.hu/.../anonim-hatarozatok-tara` link redirects to `birosag.hu/ugyfeleknek/birosagi-hatarozatok-gyujtemenye`. The Constitutional Court (`alkotmanybirosag.hu`) is reachable. Tier C.

## Slovenia
- **Legislation:** PIS `pisrs.si` is an Angular SPA. Its config (`/assets/config.json`) exposes `BACKEND_ENDPOINT: https://pisrs.si/api`, with routes such as `/navigation`, `/gethtml/{id}` and `/filter/`. Endpoints are undocumented and untested. ID: `ZAKO1263`-style codes (OZ). Tier C.
- **Case law:** sodnapraksa.si is a Vue SPA. `config.js` gives `apiUrl https://sodnapraksa.si/backend/api/` and Keycloak (`sp-realm`). The search state is a base64 JSON in the URL, including `similarityCutoff`/`similarityTopK`, so it has **semantic search**. Covers VSRS, VDSS, higher courts, and the Constitutional Court. Tier C (backend unverified). `us-rs.si` returns 403 from the UK.

## Croatia
- **Legislation:** Narodne novine. ELI `https://narodne-novine.nn.hr/eli/sluzbeni/2018/42/805` redirects (302) to `/clanci/sluzbeni/2018_05_42_805.html`. Verified. This is gazette text, **not consolidated**; zakon.hr is a private consolidated mirror (reachable). MCP: MateMatic `hr-eli-mcp`. Tier C.
- **Case law:** `sudskapraksa.csp.vsrh.hr` redirects (301) to **`odluke.sudovi.hr`**, whose **robots.txt is `Disallow: /`** apart from the About and help pages. Tier **D** if we honour robots. The Constitutional Court (`usud.hr`) is HTML and reachable.

## Bulgaria
- `legalacts.justice.bg` (central portal for court acts), `vks.bg` (Supreme Court of Cassation) and `pravo.bg`: **time out from the UK**.
- `dv.parliament.bg` (State Gazette): a JSF app (`/DVWeb/index.faces`), 200.
- `lex.bg`: private, 200, consolidated text, with terms likely restricting scraping (unverified).
- Tier D/C.

## Serbia
- `pravno-informacioni-sistem.rs`: the state legal information system, free, SPA. 302 → 200.
- `vrh.sud.rs/sr-lat/sudska-praksa`: Supreme Court practice HTML, 200.
- `paragraf.rs`: commercial.
- Tier C. Unverified beyond reachability.

## Bosnia & Herzegovina
- `pravosudje.ba` / `csd.pravosudje.ba` (VSTV case-law database) redirects to `/vstvfo/...`. Historically subscription-based, so treat as D (unverified).
- `ustavnisud.ba` (Constitutional Court): HTML, 200, tier C.
- Gazettes (`sluzbenilist.ba`) are paid (unverified).

## North Macedonia
- `slvesnik.com.mk` (Official Gazette): 301 → paid subscription for search (unverified).
- `sud.mk` and `pravo.org.mk`: **time out from the UK**.
- Tier D.

## Albania
- `qbz.gov.al` (Official Publications Centre, Angular SPA, 200). It hosts the Fletorja Zyrtare and consolidated texts. Tier C.
- `gjykataelarte.gov.al` (High Court, 301 → `/sq/`). HTML. Tier C.

## Montenegro
- `sluzbenilist.me` (Official Gazette, 200, tier C).
- `sudovi.me` (court portal with decisions) returns **403 from the UK**, so tier D from the UK.

## Kosovo
- `gzk.rks-gov.net` (Official Gazette, 266 KB HTML, 200, tier C).
- `gjyqesori-rks.org` (Judicial Council, decisions) returns **403 from the UK**.

## Moldova
- `legis.md` (State Register of Legal Acts) returns **403 (WAF) from the UK** on both the home page and `/cautare/getResults?doc_id=`. Tier D from the UK.
- `instante.justice.md/ro/hotaririle-instantei` (court decisions, HTML, 200) and `csj.md` (Supreme Court) are reachable. Tier C.

## Georgia
- `matsne.gov.ge` (Legislative Herald): `/{ka|en}/document/view/{id}` gives full consolidated HTML (3.6 MB for id 31702). `/en/document/search?query=` gives HTML search (1.1 MB). Verified 200. Official English translations exist for major codes. Tier C.
- Case law: `supremecourt.ge` and `ecd.court.ge` are reachable HTML. Tier C.

## Armenia
- `arlis.am` (legal information system, 200, large HTML, tier C).
- `datalex.am` (court decisions) **times out from the UK**.
- `court.am`: 200.

## Azerbaijan
- `e-qanun.az` (Next.js; `/framework/{id}`, 200; tier C).
- `supremecourt.gov.az` and `courts.gov.az` **time out from the UK**. Tier D.

## Kazakhstan
- `adilet.zan.kz` (Ministry of Justice legal database, Vue SPA shell, 1.5 KB; e.g. `/rus/docs/K940001000_` = Civil Code). The backend API is unverified. Tier C.
- `office.sud.kz` (judicial acts search) **times out from the UK**. `sud.gov.kz`: 200.

## Russia
- **Legislation (official publication):** `publication.pravo.gov.ru`. **Tier A, verified.**
  - Example: `GET http://publication.pravo.gov.ru/api/Documents?PageSize=10&Index=1&SortedBy=6&SortDestination=1`, or `?Name=...` for title search. JSON items carry eoNumber, complexName, and publishDate. PDFs per document.
  - Federal and regional acts, from 2011 onward. **Not consolidated.**
- **Consolidated legislation:** `pravo.gov.ru` IPS **times out from the UK**.
- **Case law:**
  - `sudact.ru`: private aggregator, 200, but results are loaded by JS / captcha (no doc links in the HTML).
  - `kad.arbitr.ru` (arbitrazh case files): 200, known anti-bot (wasm/cookie) protection.
  - `vsrf.ru` and `bsr.sudrf.ru` (judicial practice): **time out from the UK**.
  - Tier D/C.

---

## Build priorities (suggested)

1. **Turkey:** reimplement on Bedesten (case law + mevzuat), AYM KBB, and UYAP Emsal. All are verified JSON and keyless, with a shared 1 req / 3.5 s limiter for Bedesten. Add Danıştay direct, Rekabet, Sayıştay and KİK later as HTML adapters.
2. **Czechia:** e-Sbírka sbr-cache (search + fragment) and rozhodnuti.justice.cz (by-date + finaldoc). NSS/ÚS HTML later.
3. **Poland:** Sejm ELI (search/struct/text) plus SAOS (common courts only). Flag SN, TK and NSA as gaps unless we accept HTML scraping and the NSA robots issue.
4. **Ukraine:** reyestr HTML search + Review. Legislation needs a UA/EU egress proxy.
5. **Romania:** SOAP adapter is ready but blocked by the provider outage and the UK WAF. Re-test.

Small jurisdictions are mostly HTML-only or blocked from the UK. Do them only with an EU egress and per-site robots review.
