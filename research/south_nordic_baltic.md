# South / Nordic / Baltic — live legal data sources

Research date 2026-11-05. "verified" = hit with curl (Chrome UA, GET/simple POST, a handful of calls) on 2026-11-05 from a UK residential IP.
Tiers: **A** official API, no key · **B** official API, free key · **C** HTML/undocumented-JSON only, automated access not forbidden · **D** paid / forbidden (ToS or robots `Disallow: /`) / blocked / nothing usable.
"Undocumented JSON" = the JSON backend a public SPA calls; works without a key but has no contract and can change without notice. I put it in tier C, not A.

## Summary

| Jurisdiction | Case law | Legislation | Best endpoint(s) | Auth | Notes |
|---|---|---|---|---|---|
| **Spain** | C (ToS restricts) | **A** | `boe.es/datosabiertos/api/legislacion-consolidada` · CENDOJ `poderjudicial.es/search/search.action` (POST) | none | BOE has a per-article consolidated API (very good). CENDOJ terms say "personal use only, no bulk download, no commercial use". |
| **Portugal** | C | C | `dgsi.pt/{db}.nsf/...?SearchView&Query=` · `diariodarepublica.pt` (OutSystems SPA) | none | DGSI is old Lotus Domino, but full-text search works by GET. DRE is a JS SPA with no documented API. |
| **Italy** | D (Cassazione unreachable) / A-bulk (Corte cost.) | **A** (search) + C (text) | `api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1/ricerca/semplice` (POST) · `normattiva.it/uri-res/N2Ls?urn:nir:...` | none | Normattiva open-data API: search + bulk collections. Italgiure timed out (TCP), likely blocked outside Italy. |
| **Ireland** | D (robots `Disallow: /`) | **A**-ish (eISB ELI XML, as enacted) + C (revised) | `irishstatutebook.ie/eli/{y}/act/{n}/enacted/en/xml` · `judgments.courts.ie/judgments?q=` | none | Consolidated text only via the Law Reform Commission Revised Acts (HTML). |
| **Malta** | D (Cloudflare blocks) | C (PDF) | `legislation.mt/eli/cap/{n}/eng/pdf` | none | Consolidated chapters come only as PDF. eCourts returns Cloudflare "you have been blocked". |
| **Cyprus** | D | C/D | `cylaw.org` (Cyprus Bar Association, not official) | none | CyLaw ToS and robots forbid robots on case law. Laws are mostly as-enacted PDFs. |
| **Greece** | C | C (undocumented JSON) | `searchetv99.azurewebsites.net/api/simplesearch` (POST, ET/FEK) · `areiospagos.gr/nomologia/apofaseis_result.asp` | none | No consolidated official text (only the FEK gazette). Diavgeia has a real API, but it covers administrative acts, not law. |
| **Denmark** | C (undocumented JSON) | **A** | `retsinformation.dk/eli/{...}/xml` · `api.retsinformation.dk/v1/Documents?date=` · `domsdatabasen.dk/webapi/api/Case/search?query=` | none | Domsdatabasen coverage is thin (mostly 2022 onward). |
| **Sweden** | **A**-ish (undocumented but clean REST) | **A** | `rattspraxis.etjanst.domstol.se/api/v1/sok` (POST) · `data.riksdagen.se/dokumentlista/?doktyp=sfs` | none | Best case-law source in this region. Full text inline in JSON. |
| **Norway** | C (Supreme Court on domstol.no) / D (Lovdata) | A-bulk (NLOD) / B-paid per-doc | `api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2` | none (bulk) / paid key (API) | lovdata.no robots: `User-agent: * Disallow: /`. Free data is bulk only. |
| **Finland** | C (HTML) | **A** | `opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/{y}/{n}` | none | **Court judgments are NOT in the open-data API or ZIPs.** Paging changes to keyset in week 47 (2026) and will break existing clients. |
| **Iceland** | **A**-ish (undocumented GraphQL) | D (Cloudflare challenge) | `island.is/api/graphql` `webVerdicts` / `webVerdictById` | none | Supreme Court, Landsréttur and district-court verdicts, full text. althingi.is law pages sit behind a Cloudflare JS challenge. |
| **Estonia** | D (robots disallow) | C (undocumented JSON/XML) | `riigiteataja.ee/public-api/api/v1/akt/{id}` + `/xml` | none | RT was relaunched as an Angular SPA. The old `/akt/{id}.xml` URLs now return the SPA. |
| **Latvia** | A-bulk (CC0 CSV index + PDF) | C (HTML) | `dagr.gov.lv/public/kkp_prod_anon_nolemumi?filename=...csv` · `likumi.lv/ta/id/{id}` | none | No programmatic full-text case search. manas.tiesas.lv timed out. |
| **Lithuania** | C (LITEKO ASP.NET, unverified) | D (Cloudflare challenge) | `liteko.teismai.lt/viesasprendimupaieska/` | none | e-TAR, e-seimas and lat.lt all return a Cloudflare challenge. data.gov.lt's WAF blocked our IP. |

Biggest takeaways: **Spain-BOE, Denmark, Sweden, Finland (legislation) and Italy-Normattiva are real APIs.** Sweden (domstol) and Iceland (island.is) have clean keyless JSON for case law. Lithuania, Malta and Iceland-legislation are effectively blocked by Cloudflare. Norway's Lovdata forbids robots site-wide and only offers bulk free data.

---

## Spain

### Legislation — BOE Datos Abiertos (tier A, verified working 2026-11-05)
- Base: `https://www.boe.es/datosabiertos/api/`. **Gotcha: you must send `Accept: application/json` or `application/xml`.** Without it you get `400 "No soportado ningún mime type de la cabecera Accept"`.
- Search consolidated legislation (Elasticsearch `query_string` passed as a URL-encoded JSON `query` parameter):
  `GET /legislacion-consolidada?limit=2&query={"query":{"query_string":{"query":"titulo:enjuiciamiento"}}}` → JSON with `identificador` (e.g. `BOE-A-2000-323`), `rango`, `titulo`, `fecha_actualizacion`, `url_eli`.
  - `texto:desahucio` works (full-text search). `materia:"Arrendamientos"` returned `500 Server error - Code: 101`, so some field syntaxes fail.
- Table of contents: `GET /legislacion-consolidada/id/BOE-A-2000-323/texto/indice` (XML; each block has an `id` such as `a1`, `preambulo`, `dt1`).
- **Per-article, consolidated**: `GET /legislacion-consolidada/id/BOE-A-2000-323/texto/bloque/a1` → `<bloque id="a1" tipo="precepto" titulo="Artículo 1"><version fecha_vigencia=...>`. Keeps historical versions per block.
- Other endpoints: `/legislacion-consolidada/id/{id}/metadatos`, `/analisis`, `/metadata-eli`, `/texto` (full). Daily gazette summary: `GET /boe/sumario/20261104`.
- ELI: `https://www.boe.es/eli/es/l/2000/01/07/1/con` (HTML, 2.7 MB).
- Coverage: state law plus autonomous-community law; Spanish only (some co-official languages exist for gazette items).
- Licence: BOE open-data reuse terms (attribution; consistent with Ley 37/2007 reuse). robots.txt is huge but only blocks lang variants and specific docs. No published rate limit; unverified.
- Existing MCPs: `AnCode666/boe-mcp` (MIT, ★6), `Proxera-Group/boe-mcp`, `QuantumBBoy/boe-mcp` (MIT). Several exist, so check one before building.

### Case law — CENDOJ / poderjudicial.es (tier C, ToS-restricted; verified working 2026-11-05)
- All Spanish courts (TS, AN, TSJ, AP, first instance selectively), roughly 1990s → today, Spanish plus co-official languages.
- No API. Search is a form POST that returns an HTML fragment:
  `POST https://www.poderjudicial.es/search/search.action` with body `action=query&sort=IN_FECHARESOLUCION:decreasing&recordsPerPage=10&databasematch=TS&start=1&TEXT=desahucio`, sending the cookie from `GET /search/indexAN.jsp` plus `Referer` and `X-Requested-With: XMLHttpRequest`.
  → "9434 resultados (máximo documentos a recuperar 200)" with ROJ, ECLI, Sala, Ponente and summary. **Gotcha:** `sort=...:decreciente` returns "La búsqueda no es válida!"; it must be `decreasing`. A plain GET to `search.action` returns 403. Only 200 hits are retrievable per query.
  - Other form fields: `ECLI`, `ROJ`, `NUMERORESOLUCION`, `NUMERORECURSO`, `PONENTE`, `JURISDICCION`, `ANYO`, `databasematch` (`TS`, `AN`, …).
- Document: `GET /search/TS/openDocument/{hash}/{yyyymmdd}` (HTML wrapper; the PDF link is inside).
- robots.txt: `Crawl-delay: 5`, search path not disallowed.
- **ToS (verified text on the search page):** "podrá consultar los documentos siempre que lo haga para su uso particular. No está permitida la utilización de la base de datos para usos comerciales, ni la descarga masiva… La reutilización… para la elaboración de bases de datos o con fines comerciales debe seguir el procedimiento… del CGPJ". A live, per-query, non-commercial open-source tool is a grey zone, not clearly allowed.
- Existing: `ComputingVictor/MCP-CENDOJ` (★18, no licence, updated 2026-11-04), `Gasparms9/Project5-Cendoj-Scrapping-API`.

## Portugal

### Case law — DGSI (tier C; verified working 2026-11-05)
- `https://www.dgsi.pt/` runs on Lotus Domino. One database per court: `jstj.nsf` (STJ), `jsta.nsf` (STA), `jtrl/jtrp/jtrc/jtrg/jtre.nsf` (Relação courts), `jtca/jtcn.nsf` (TCA), `atco1.nsf` (Tribunal Constitucional mirror). Coverage is roughly 1950s–today; it is a selection, not every decision.
- **Full-text search by GET:** `https://www.dgsi.pt/jstj.nsf/954f0ce6ad9dd8b980256b5f003fa814?SearchView&Query=arrendamento&SearchMax=5` → HTML table (date, processo, relator, descritores) plus links `/jstj.nsf/954f0ce6.../{docUNID}?OpenDocument`. Supports Domino query syntax (`AND`, `OR`, `FIELD x CONTAINS y`). Default ordering is relevance; add `&SearchOrder=4` for date order (unverified). Recent list: `?OpenView&Count=N`.
- Encoding: mixed ISO-8859-1 / UTF-8. Pages are tagged `<meta name="robots" content="noindex">` and robots.txt returns 404. No explicit ToS against automated access found (unverified).
- Existing: `leviathanch/fetch_dgsi_pt` (2025, no licence), `MowlyAI/pt-caselaw-dgsi`.

### Legislation — Diário da República (tier C; partially verified)
- `https://diariodarepublica.pt/dr/...` is an OutSystems SPA: every page returns the same 2.3 KB JS shell, so there is **no server-rendered HTML** and a headless browser or the internal `screenservices` JSON is required (not reverse-engineered here).
- ELI resolves: `https://data.dre.pt/eli/lei/7/2009/02/12/p/dre/pt/html` → 302 → `/dr/detalhe/lei/7-2009-602073` (verified). Consolidated text exists on the site ("legislação consolidada"), e.g. `/dr/legislacao-consolidada/lei/2009-34546475`.
- `diariodarepublica.pt/robots.txt` returns the SPA error page. dados.gov.pt has no DRE dataset (verified empty search).
- Existing MCP: none found.

## Italy

### Legislation — Normattiva (search tier A, text tier C; verified working 2026-11-05)
- **Open-data API** (no key; base URL from `dati.normattiva.it/assets/env.js`): `https://api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1/`
  - `POST ricerca/semplice` with body `{"testoRicerca":"silenzio assenso","orderType":"vecchio"|"recente","paginazione":{"paginaCorrente":1,"numeroElementiPerPagina":10}}` → `listaAtti[]` (codiceRedazionale, dataGU, descrizioneAtto, titoloAtto) plus `numeroAttiTrovati` (65 for "silenzio assenso").
  - Also `ricerca/avanzata`, `ricerca/predefinita`, `ricerca-asincrona/{nuova-ricerca,check-status,conferma-ricerca}` (async bulk export), `collections/collection-predefinite` (verified; formats O = original, M = multivigente, V = vigente), `collections/download/collection-preconfezionata`, `tipologiche/*`.
- Per-act/article text: HTML via URN. `https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1990-08-07;241` (L. 241/1990) and `...;241~art3` (single article). `!vig=YYYY-MM-DD` sets the point in time. Akoma Ntoso export: `/do/atto/caricaAKN?dataGU=19900818&codiceRedaz=090G0294&dataVigenza=20261105` returned an HTML page, not raw AKN, so it needs more work.
- robots: `/ricerca/` disallowed, `/` allowed. Licence: CC BY 4.0 per the Normattiva open-data notes (unverified on page).
- Existing: `SimonBerg255/gov-it-legal-mcp` (MIT, ★11; Normattiva plus administrative-court rulings), `adellorto/normattiva-mcp` (MIT), `cybermerlo/normattiva-mcp` (MIT, uses the open-data API), `ondata/normattiva_2_md` (MIT, ★23).

### Case law
- **Corte di Cassazione — Italgiure / SentenzeWeb** (`www.italgiure.giustizia.it/sncass/`): **TCP connect timeout on 80 and 443** (IP 81.126.56.168) from the UK. Probably geo- or IP-filtered. Known undocumented Solr endpoint `POST /sncass/isapi/hc.dll/sn.solr/sn-collection/select?app.query` (unverified). It is free and covers the last 5 years of civil and criminal decisions (unverified). Treat as **D** until it can be tested from an Italian IP. Existing: `Mike-1010/italgiure-mcp`, `TomatoChat/ItalgiureCivileScraper` (MIT).
- **Corte costituzionale** — `dati.cortecostituzionale.it`: bulk ZIPs (verified links) `opendata/distribuzione/pronunce/P_json2001_oggi.zip`, `P_csv…`, `CC_OpenPronunce_1981_2000.zip`, covering ~20,000 decisions from 1956. The SPARQL endpoint returned an empty body. Main site `cortecostituzionale.it` sits behind a **Radware captcha**. Tier A for bulk, D for live.
- **Administrative justice** (`giustizia-amministrativa.it`): HTML reachable (200). OpenGA dataset is used by `gov-it-legal-mcp`. Not probed further.

## Ireland

### Legislation (verified working 2026-11-05)
- **eISB (Irish Statute Book), ELI, as enacted:** `https://www.irishstatutebook.ie/eli/2014/act/30/enacted/en/xml` (XML, 320 KB), `/eli/2014/act/30/section/2/enacted/en/html` (**per-section**). SIs: `/eli/{y}/si/{n}/made/en/xml`. robots.txt returns 404, so nothing is disallowed. Tier A-ish: static ELI with no search API.
- **Consolidated:** Law Reform Commission Revised Acts `https://revisedacts.lawreform.ie/eli/2014/act/30/revised/en/html` (HTML, 725 KB). Not every Act is revised. Tier C.
- **Oireachtas API** (bills and Acts metadata, tier A): `https://api.oireachtas.ie/v1/legislation?bill_status=Enacted&limit=1` → JSON (4,070 bills).
- Existing: `matematicsolutions/ie-eli-mcp` (Apache-2.0, 2026-09).

### Case law — Courts Service (tier D by robots; endpoint works)
- `https://judgments.courts.ie/judgments?q=judicial+review+planning` → "3,321 results found" (verified). Filters: `courtIds`, `dateFrom`, `dateTo`, `judge`, `neutralCitation`. Document `/judgments/{id}`, file `/judgments/documents/{docId}/download`.
- **robots.txt: `User-agent: * Disallow: /`** and the page carries meta `noindex, nofollow`. Covers Supreme Court, Court of Appeal and High Court (~2001 onward; unverified).
- BAILII Irish collection (`bailii.org/ie/`) is now behind an Anubis anti-bot proof-of-work page. Tier D.

## Malta
- **Legislation:** `https://legislation.mt/eli/cap/16/eng` (Civil Code) → redirects to `/eli/cap/16/eng/portalpdf` (HTML wrapper); `/eli/cap/16/eng/pdf` → 5.2 MB PDF of the consolidated chapter (verified). `/xml` → wrapper; `/html` → error page. Languages `eng` and `mlt`. ELI RDFa in the page. robots only blocks Sogou. **Tier C (PDF only, consolidated, whole document only).** Existing: `lexifina/malta-acts` (git history of amending Acts).
- **Case law:** `https://ecourts.gov.mt/onlineservices/Judgements` → **403 Cloudflare "Sorry, you have been blocked"** (verified). **D.**

## Cyprus
- **CyLaw** (`cylaw.org`, run by the Cyprus Bar Association, **not official**). **robots: `Disallow: /apofaseis/ /apofaseised/ /clr/ /cgi-bin/`**, which covers all case law. A direct GET of a judgment URL returned 403. ToS (Greek, verified) explicitly says CyLaw is not a source for services reusing its content and restricts robots/"external indexing" on case law. **Case law: D.**
- Legislation: `/nomoi/arith_index.html` → per-year index → `/nomoi/arith/2016_1_014.pdf` (as-enacted PDFs). Some consolidated HTML under `/nomoi/enop/` (the test URL returned 404). Encoding windows-1253. **C/D** given the ToS stance. No official open legislation API found (unverified).
- Existing: only small scrapers (`RokibMondol/cylaw.org_webscrapping`, `KGeorgiadis-law/cyprus_law_twitterbot` GPL-3).

## Greece
- **Legislation — National Printing House (ET/FEK):** `search.et.gr` is a React app on top of an **undocumented JSON API** `https://searchetv99.azurewebsites.net/api` (found in `main.*.js`). Verified:
  `POST /api/simplesearch` with body `{"selectYear":["2024"],"documentNumber":"4","selectIssue":["1"]}` → `{"status":"ok","data":"[{\"search_ID\":\"760949\",\"search_PrimaryLabel\":\"Α 4/2024\",...}]"}` (data is a JSON *string*). Other routes: `/searchlegislation`, `/searchbydate`, `/searchkad`, `/tags`, `/namedentity`. FEK PDFs are on the blob store `ia37rg02wpsa01.blob.core.windows.net` (unverified path). robots allows all. **Gazette only, no official consolidated text.** Tier C.
- **Diavgeia** (`diavgeia.gov.gr/opendata/search.json?q=...`, verified JSON, no key) is a real API but holds administrative decisions, not statutes or case law.
- **Case law — Areios Pagos** (Supreme Civil/Criminal Court): `https://www.areiospagos.gr/nomologia/apofaseis.asp` → form POST to `apofaseis_result.asp?S=1` (fields `X_TMHMA`, `X_SUB_TMHMA`, `x_number`, `x_ETOS`). Search is by number, year and chamber; a free-text field was not found. windows-1253. robots.txt 404. Tier C. Council of State (`adjustice.gr`, Oracle WebCenter) was not probed beyond the redirect.
- Existing: `Phlorion/AreiosPagosDataAnalysis` (crawler). No MCP found.

## Denmark
### Legislation — Retsinformation (tier A; verified working 2026-11-05)
- ELI XML (LexDania schema): `https://www.retsinformation.dk/eli/lta/2024/1158/xml` (also `/html`, `/pdf`). `lta` = Lovtidende A. Consolidated acts (LBK) and the full history are available.
- Official change feed: `https://api.retsinformation.dk/v1/Documents?date=2026-11-04` → JSON list of changed docs with `href` to `/eli/accn/{accession}/xml`. Documented restrictions (unverified this session): only callable between 03:00 and 23:45 CET, and about 1 request per 10 s.
- Search (undocumented JSON used by the site): `https://www.retsinformation.dk/api/documentsearch?t=lejeloven&ps=2` → `resultCount` 1337, with `popularTitle`, `shortName` "LOV nr 341 af 22/03/2022" and `id`.
- robots: sitemap only. Licence: free reuse (unverified).
- Existing: `OneCodeApS/retsinformation-api-mcp` (2026-11), `Ansvar-Systems/Danish-law-mcp` (Apache-2.0), `mfhens/retsinformation`, `lkarlslund/lovkilde` (MIT, ★15).
### Case law — Domsdatabasen (tier C / undocumented JSON; verified working)
- `GET https://domsdatabasen.dk/webapi/api/Case/search?query=lejem%C3%A5l&pageSize=2&currentPage=1` → `totalCount` 464, `cases[]` (courtCaseNumber, officeName, caseSubjects, `documents[]` with `ecli`, `verdictDateTime`, `firstPageHtml`). The parameter must be `query` (`searchText` returns 0 results). POST returns 405.
- Run by Domstolsstyrelsen since 2022 with prospective publication, so **coverage is thin before 2022**. Højesteret also publishes on `hoejesteret.dk` (HTML; not probed).
- Existing: `alexandrainst/domsdatabasen` (MIT).

## Sweden
### Case law — Domstolsverket "Rättspraxis" (tier A-ish: keyless REST, undocumented; verified working 2026-11-05)
- `POST https://rattspraxis.etjanst.domstol.se/api/v1/sok` with JSON body `{"sokfras":{"andLista":["hyresavtal"],"orLista":[],"notLista":[],"exaktFras":""},"antalPerSida":20,"sidIndex":0,"asc":false,"sortorder":"avgorandedatum","filter":null}` → `publiceringLista[]` with **full text in `innehall` (HTML)**, `domstol.domstolKod` (HDO, HFD, HYOD, …), `malNummerLista`, `lagrumLista`, `forarbeteLista` and attached PDFs.
- Other routes (from the Angular bundle): `GET /api/v1/publiceringar` (latest; 765 KB, `antal` ignored), `/api/v1/publiceringar/{id}`, `/api/v1/publiceringar/grupp/{id}`, `/api/v1/bilagor/{lagringId}` (PDF), `/api/v1/domstolar`, `/api/v1/sokforfiningar`. No swagger found.
- Covers precedents and other published decisions from HD, HFD, the appeal courts, MÖD, AD and others. Swedish only.
- Lagrummet.se (portal) exists. Lagen.nu (`staffanm/ferenda`, BSD-2, ★38) is the established open-source parser; `staffanm/para-text` says lagen.nu has an "open API".
### Legislation — Riksdagen open data (tier A; verified working)
- Search: `https://data.riksdagen.se/dokumentlista/?sok=hyresavtal&doktyp=sfs&utformat=json&sz=2` → 44 hits.
- Text: `https://data.riksdagen.se/dokument/sfs-1970-994.text` (Jordabalken, **consolidated** "Ändrad: t.o.m. SFS 2026:1498"), also `.html` and `.json`. Whole document only; split on `N §` yourself.
- Regeringskansliet's SFS database `beta.rkrattsbaser.gov.se/sfs/item?bet=1970:994` (HTML, meta `noindex`).
- Licence: Riksdagen open data is free with no key; the old 1 request/second guidance is unverified.
- Existing: `Ansvar-Systems/Swedish-law-mcp` (Apache-2.0), `amrtini/riksdagen-mcp-server` (MIT), `kajmund/lagen-nu-mcp`.

## Norway
### Legislation — Lovdata (verified working 2026-11-05)
- **Free public data (NLOD 2.0), bulk only:** `GET https://api.lovdata.no/v1/publicData/list` → files `gjeldende-lover.tar.bz2` (5.8 MB, updated daily), `gjeldende-sentrale-forskrifter.tar.bz2` (21.5 MB), `lovtidend-avd1-2001-2025.tar.bz2`, `lovtidend-avd1-2026…`, `avd2…`. Download: `/v1/publicData/get/{filename}`. XML-compatible HTML with chapters, § and ledd. **Tier A for bulk.** Re-downloading 5.8 MB per call is feasible but is effectively "bulk".
- Per-document Lovdata API (`/v1/structuredRules/...` → 401) is **commercial and needs a key** (marketed with an SLA): B/paid.
- **lovdata.no robots.txt: `User-agent: * Disallow: /`** (plus explicit GPTBot/ChatGPT-User bans). `/sok` returns "405 Request stopped by Varnish IPS". HTML scraping of lovdata.no is **D**.
### Case law
- Lovdata free covers Supreme Court decisions, but robots forbids it: **D**. Lovdata Pro is paid.
- `https://www.domstol.no/no/hoyesterett/avgjorelser/` → redirects to `/avgjorelser-2026/` (verified 200). Supreme Court decisions are listed with PDFs, current years only, with no search API. **C.**
- Existing: `NationalLibraryOfNorway/lovdata-public-conversion-script`, `sondreskarsten/norwegian-laws` (MIT; laws as git history from the NLOD API), `Ansvar-Systems`-style `ngu-tek/Norwegian-law-mcp` and `rogulus/Norwegian-law-mcp` (Apache-2.0).

## Finland
### Legislation — Finlex avoin data (tier A; verified working 2026-11-05)
- OpenAPI spec: `https://opendata.finlex.fi/v3/api-docs` (Swagger UI at `/swagger-ui/index.html`). Base `https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/`.
- `GET act/statute-consolidated/list?format=json&limit=2` (max 10 per page) → `akn_uri` + status. Filters: `startYear`, `endYear`, `publishedSince`, `dateIssued`, `langAndVersion` (`fin@`, `swe@`, `fin@20240101`), `keyword` (keyword list; **not** full text; `keyword=vuokra` returned `[]`), `titleContains` (on non-list routes).
- `GET act/statute-consolidated/1889/39-001` → Akoma Ntoso (6.6 MB, all versions). `act/statute-consolidated/1999/731` (Constitution) → 200, 373 KB. Language/version: `/{y}/{n}/fin@/main.akn`, `main.pdf`.
- Types: `act/statute`, `act/statute-consolidated`, `doc/authority-regulation`, `doc/government-proposal`, etc.
- **Breaking change announced:** week 47/2026 `page` → keyset `lastSeen=/akn/fi/act/...`.
- Daily ZIP bulk (`statute-consolidated.zip` 4.1 GB, etc.). Licence CC BY 4.0 (unverified on page). `User-Agent` header is a declared parameter.
- No per-section endpoint; split the AKN XML yourself (AKN `section`/`subsection` elements carry eIds).
### Case law — **not in open data** (surprise)
- The API exposes `judgment/{type}`, but every type I tried returned 404 (`kko`, `kho`, `supreme-court-precedent`, …). The download page (verified) lists only "Oikeuskäytäntö kirjallisuudessa" (case-law references in literature), **no KKO/KHO judgments**.
- HTML: `https://www.finlex.fi/fi/oikeuskaytanto/korkein-oikeus/ennakkopaatokset/2025/1` (KKO:2025:1, Next.js, 265 KB; verified). Year lists at `/ennakkopaatokset/{year}`. robots only disallows `/_next/image`. **Tier C.**
- Legacy "Semantic Finlex" SPARQL `http://ldf.fi/finlex/sparql` still answers but appears stale (a `dateIssued` max query returned empty). Don't rely on it.
- Existing: `akunikkola/claude-for-legal-finland` (MIT, ★115), `OJHela/finlex-mcp` (2026-11), `annasebedash-creator/finlex-mcp`, `NectiaAutomation/finlex-mcp-server` (MIT).

## Iceland
### Case law — island.is (tier A-ish: keyless GraphQL, undocumented; verified working 2026-11-05)
- haestirettur.is and landsrettur.is now redirect to `https://island.is/domar?court=...`.
- `POST https://island.is/api/graphql` with `{"query":"query { webVerdicts(input:{searchTerm:\"leigusamningur\"}) { total items { id title caseNumber verdictDate court } } }"}` → `total` 1385, with Landsréttur, Hæstiréttur and district-court items.
- Full text: `query { webVerdictById(input:{id:"g-…"}) { item { title court richText pdfString } } }` (`content`, `html` and `text` fields do not exist). Introspection is disabled.
- Icelandic only. No explicit ToS found (unverified).
### Legislation — Alþingi lagasafn (tier D in practice)
- `https://www.althingi.is/lagas/nuna/1994036.html` and `/lagasafn/zip-skra-af-lagasafni/` → **403 Cloudflare "Just a moment…" JS challenge** (verified).
- Parliamentary XML still works: `https://www.althingi.is/altext/xml/thingmalalisti/?lthing=157` (bills, not consolidated law).
- Existing: `busla/althingi-rest-api`, `bjornlevi/5thpower` (MIT) are scrapers for parliamentary data. No law MCP found.

## Estonia
### Legislation — Riigi Teataja (tier C, undocumented JSON/XML; verified working 2026-11-05)
- The site is now an Angular SPA: every `/akt/...` URL (including the old `/akt/{id}.xml`) returns the 61 KB SPA shell.
- **Backend:** `https://www.riigiteataja.ee/public-api/api/v1/`
  - `GET akt/104012024004` → JSON metadata (Kohtute seadus: `tekstiliik: terviktekst`, `aktiStaatus`, `grupiId`, validity dates).
  - `GET akt/104012024004/xml` → **full consolidated act XML** (`<oigusakt>`, tyviseadus schema, 470 KB; per-§ structure inside).
  - `GET en/akt/504042014002` → English translation metadata. `avalik/rtOsad` lists gazette parts.
  - The same ID returns 404 on the non-`en` route if it is a translation ID. Note the `NULL akt SOLR-st` error text.
- **Search endpoint not found** in the bundle (Angular router paths only). Discovering act IDs needs the search UI's XHR (not reverse-engineered). The ELI `.../eli/ee/Riigikogu/act/{id}/consolide` redirects to `/en/akt/{id}`.
- robots: `Disallow: */kohtulahendid/*` and `*/kohtuteave/*` (court decisions), plus long lists of specific acts.
- Existing: `dustinest/riigiteataja_ee_ai_mcp` (MIT, ★4; search plus full text, so check how it searches), `OJHela/riigiteataja-mcp`, `HeaNimi/riigiteataja-offline`.
### Case law (tier D by robots)
- Riigi Teataja hosts all-instance decisions under `/kohtulahendid/`, but robots disallows it. PDF route seen in the bundle: `/public-api/api/v1/kohtuteave/kohtulahendid/{id}/file`.
- Supreme Court: `riigikohus.ee/et/lahendid` → `https://rikos.rik.ee/Lahendid?otsisona=...` (HTML list; verified 200), but **rikos robots: `Disallow: /`**.

## Latvia
### Case law (verified working 2026-11-05)
- **Open data (CC0):** data.gov.lv CKAN `package_search?q=tiesu+nolemumi` → "Anonimizētie nolēmumi" (Tiesu Administrācija; metadata updated 2026-11-05; years 2007–2026).
  CSV: `https://dagr.gov.lv/public/kkp_prod_anon_nolemumi?filename=kkp_prod_anon_nolemumi.csv` with columns `MaterialFileId, Court, CourtDepartment, EcliCode, CaseNumber, …, RegistrationDate, Status, CourtInstance, DownloadUrl`.
  Each row → `https://gateway.elieta.lv/api/v1/PublicMaterialDownload/{uuid}` → **PDF** (verified).
  This is a metadata index plus PDFs, with **no full-text search**. The CSV is large (size not checked). **Tier A for bulk, no live search.**
- `manas.tiesas.lv/eTiesasMvc/nolemumi` (official search UI) → **connection timeout** (probably geo/IP filtered). `at.gov.lv` (Supreme Court) archive pages return HTML 200.
### Legislation — likumi.lv (tier C; verified working)
- `https://likumi.lv/ta/id/225418-civillikums` → HTML (1.3 MB), consolidated, with per-paragraph anchors. robots disallows `/search.php*`, `/doc.php/*`, `/*/redakcijas-datums/` (historical versions), `/rss/`, but allows `/ta/id/`. No API or XML. Publisher: Latvijas Vēstnesis. Reuse terms unverified.
- data.gov.lv has translation datasets (LV→EN laws, Valsts valodas centrs) but no likumi.lv text dump.
- Existing: `viktor-gusev/blame-likumi.lv` (git blame of laws), `andrejsboka/likumi-monitor`.

## Lithuania
- **Legislation — e-TAR** (`e-tar.lt`) and **e-seimas** (`e-seimas.lrs.lt`): **403 Cloudflare "Just a moment…" challenge** on every path including robots.txt (verified). The undocumented `e-tar.lt/rs/legalact/...` was blocked the same way. **D without a headless browser.**
  - Seimas open data XML still works, CC BY 4.0: `https://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos` (verified). It covers parliamentary data, not consolidated act texts (unverified whether a legal-act text feed exists).
  - data.gov.lt / get.data.gov.lt (which publishes a TAR dataset, unverified): **our IP was blocked by the WAF** ("Attack ID 20000018").
- **Case law — LITEKO** (`liteko.teismai.lt/viesasprendimupaieska/detalipaieska.aspx`): ASP.NET WebForms (viewstate POST), page loads 200. Search was not exercised; tier C, unverified. robots.txt returns 404. Supreme Court `lat.lt` returns a Cloudflare challenge. `eteismai.lt` is a **private** aggregator (forum, lawyer directory), not official.
- Existing: `Ansvar-Systems/Lithuanian-law-mcp`, `simasrazinskas/istatym.ai` (AGPL-3, "agentic RAG over the full TAR"; worth checking how they get TAR data), `pomido-lt/pomido-plugin` (MIT).

---

### Cross-cutting notes
- **Ansvar-Systems** publishes a family of `<Country>-law-mcp` repos (Swedish, Danish, Lithuanian, plus Norwegian forks; Apache-2.0, ★0–1). Check its quality before treating it as prior art.
- Undocumented SPA backends (Normattiva BFF, Riigi Teataja public-api, ET search, domstol.se, Domsdatabasen, island.is GraphQL) are keyless and fast, but will break when the frontend is redeployed. Pin request shapes in tests.
- Geo/IP filtering hit Italgiure, manas.tiesas.lv, ecourts.gov.mt and data.gov.lt. These should be retested from an in-country IP before writing them off.
- The GitHub search for MCPs hit the API rate limit before I could query Portugal, Ireland (beyond ie-eli-mcp), Latvia, Iceland and Malta MCPs. None were found in the earlier queries that did run.
