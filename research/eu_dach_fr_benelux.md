# Legal data sources: EU, CoE/ECHR, DE, AT, CH, FR, BE, LU

Research date 2026-11-05. "Verified" means I sent a live GET/POST with a Chrome User-Agent on 2026-11-05 and got the result described. Anything else is marked **unverified**. I made only a few requests per source; I did no bulk crawling.

Tiers: **A** = official API, no key · **B** = official API, free key · **C** = HTML only, automated access allowed · **D** = paid, forbidden, or nothing usable.

## Summary

| Jurisdiction | Case law tier | Legislation tier | Best endpoint | Auth | Notes |
|---|---|---|---|---|---|
| EU (EUR-Lex/CELLAR, CJEU) | **A** (metadata/title search) / B (full-text) | **A** | `publications.europa.eu/webapi/rdf/sparql` + `publications.europa.eu/resource/celex/{CELEX}` (content negotiation) | none (SOAP full-text needs a free registration) | eur-lex.europa.eu HTML is behind an **AWS WAF JS challenge** (HTTP 202 with empty body). Use CELLAR, not EUR-Lex. CJEU judgments are in CELLAR (CELEX `6YYYYCJNNNN`). InfoCuria is now an Angular SPA with no documented API. |
| Council of Europe (ECHR HUDOC) | **A** (undocumented JSON) | n/a | `hudoc.echr.coe.int/app/query/results` | none | Undocumented but stable JSON search with full-text + Lucene-like filters. Full text via `/app/conversion/docx/html/body`. |
| Germany (federal) | **A** | **A** (NeuRIS, incomplete) + A (GII XML) | `testphase.rechtsinformationen.bund.de/v1/...` (NeuRIS) | none | NeuRIS has 84,784 federal decisions with full-text search. NeuRIS legislation has **only 5,518 laws, and BGB, StGB and GG returned no hits**, so you still need gesetze-im-internet.de (6,143 laws, XML zips + per-§ HTML). |
| Germany (state courts) | B/C (Open Legal Data, third party) | n/a | `de.openlegaldata.io/api/cases/search/` | none needed for reads (verified) | 425k cases, including OLG/LG. Not official. No official state-level API. |
| Austria (RIS) | **A** | **A** | `data.bka.gv.at/ris/api/v2.6/{Judikatur,Bundesrecht,Landesrecht}` | none | Best in region. JSON, full-text, per-§ documents, CC BY 4.0. `www.ris.bka.gv.at` returns a "Security Check" 503, so fetch content from `ogd.ris.bka.gv.at`. |
| Switzerland | **A** (entscheidsuche.ch, quasi-official NGO) / C (BGer) | **A** (fedlex SPARQL + Akoma Ntoso filestore) | `entscheidsuche.ch/_search.php` (Elasticsearch) and `fedlex.data.admin.ch/sparqlendpoint` | none | **entscheidsuche.ch already runs a public MCP server** (`https://mcp.entscheidsuche.ch/mcp`, verified). fedlex.admin.ch HTML is an SPA; use the SPARQL endpoint + filestore. |
| France | **B** (Judilibre via PISTE) | **B** (Légifrance via PISTE) | `api.piste.gouv.fr/cassation/judilibre/v1.0/*`, `api.piste.gouv.fr/dila/legifrance/lf-engine-app/*` | free PISTE OAuth2 client-credentials | legifrance.gouv.fr HTML returns a **Cloudflare 403**, and courdecassation.fr uses a JS redirect wall. There is no keyless route except bulk DILA dumps. Several MCP servers already exist (pylegifrance ★65). |
| Belgium | **C/D** | **C/D** | `juportal.be/content/{ECLI}/{FR\|NL}`; `ejustice.just.fgov.be/eli/...` | none | HTML only. **robots.txt forbids it on both sites**: Juportal disallows `/` for everyone except `DG_JUSTICE_CRAWLER`, and Justel disallows `/eli/` and `/cgi_loi/`. The pages respond fine, but automated access goes against robots.txt. Juportal publishes ECLI sitemaps (daily). |
| Luxembourg | **D** for live search (bulk ZIPs only) | **A** (Legilux SPARQL + filestore) | `data.legilux.public.lu/sparqlendpoint` | none | Consolidated Akoma Ntoso XML works. Case law has no search: justice.public.lu has a **FriendlyCaptcha**, and decisions come only as yearly ZIPs on data.public.lu (CC BY-ND). data.legilux robots.txt disallows `/eli/*` and `/filestore/*`, but the dataset is published as open data under CC-BY. |

---

## 1. EU: EUR-Lex / CELLAR / CJEU

### Legislation (and CJEU case law): CELLAR. Tier A, verified working 2026-11-05
- **SPARQL**: `https://publications.europa.eu/webapi/rdf/sparql?query=...&format=application/sparql-results+json` (Virtuoso, CDM ontology `http://publications.europa.eu/ontology/cdm#`). No auth.
  - CELEX → work: `SELECT ?w WHERE {?w cdm:resource_legal_id_celex "32016R0679"^^xsd:string}` → `cellar:3e485e15-…` ✔
  - Find consolidated versions: `FILTER(STRSTARTS(STR(?c),"02016R0679"))` on `cdm:resource_legal_id_celex` → `02016R0679-20160504` ✔
  - ECLI → CELEX: `?w cdm:case-law_ecli "ECLI:EU:C:2014:317"^^xsd:string ; cdm:resource_legal_id_celex ?c` → `62012CJ0131` (Google Spain) ✔
  - **Keyword search on titles works with Virtuoso `bif:contains`**: `?e cdm:expression_title ?t ; cdm:expression_uses_language <…/language/ENG> . ?t bif:contains "\"right to be forgotten\""` → returned CJEU AG opinion `62021CC0129` ✔. This searches **titles/metadata only, not the body text**.
- **Document content** (content negotiation on the CELEX URI):
  - `GET http://publications.europa.eu/resource/celex/32016R0679` with `Accept: application/xhtml+xml` and `Accept-Language: eng` → 200, 806 KB XHTML ✔
  - Consolidated: `.../resource/celex/02016R0679-20160504` → 200, redirects to `cellar/{uuid}.0022.03/DOC_1` ✔
  - CJEU judgment: `.../resource/celex/62014CJ0362` (Schrems I), `Accept: application/xhtml+xml` → 200 ✔. **`Accept: text/html` → 404** ("does not hold a content datastream of the requested type"). Always ask for `application/xhtml+xml` (fallback: `application/xml;notice=branch` for metadata, or PDF).
- Identifiers: **CELEX** (primary), ELI for legislation (`eli/reg/2016/679/oj`), ECLI for case law. Per-article access: no endpoint, so slice the XHTML locally (articles are `<div id="art_N">` in modern CONVEX output; older FORMEX converts differ). Consolidated text: yes (`0` prefix CELEX + date).
- Languages: all 24 EU languages via `Accept-Language` (3-letter codes: eng, deu, fra…).
- Licence: free reuse under Commission Decision 2011/833/EU (attribution). Rate limits: none published (**unverified**).
- **Gotcha:** `eur-lex.europa.eu/legal-content/...`, `/eli/...` and `/search.html` all return **HTTP 202 with an AWS WAF challenge page** (`awsWafCookieDomainList`, `challenge.js`) to curl, even with a Chrome UA. Don't build on EUR-Lex HTML.
- **Full-text search** of document bodies: EUR-Lex SOAP webservice `https://eur-lex.europa.eu/EURLexWebService` (expert-query syntax). It needs a **free EUR-Lex account + webservice registration** (tier B). The endpoint is reachable and not WAF'd: POSTing junk returned a SOAP 1.2 Fault ✔. Authenticated search is **unverified** (no credentials).

### CJEU / CURIA
- `curia.europa.eu/juris/...` now **redirects to `infocuria.curia.europa.eu/tabs/redirect/...`**, an Angular SPA ("RPEX"). I found no public API in its JS bundle. Treat CURIA as unusable, and get CJEU/General Court judgments, AG opinions and orders from CELLAR instead (CELEX sector 6: `CJ` judgment, `CC` AG opinion, `CO` order, `TJ` General Court).
- CELLAR has no body full-text search for case law (title `bif:contains` only). Workarounds: EUR-Lex SOAP (B), or Open Legal Data, which mirrors EuGH judgments (it returned `C-920/26` dated 2026-11-03 with a CELLAR source_url).

### Existing MCP servers / clients
- `cyanheads/eur-lex-mcp-server`: Apache-2.0, pushed 2026-11-04. Live CELLAR SPARQL: CELEX/ELI/ECLI/OJ-citation resolver, relations graph (amendments, consolidations, interpreting rulings by article), CJEU case search, raw SPARQL. **The most complete one; reuse or learn from it.**
- `scimorph/eur-lex-mcp` (MIT, 2026-10-24), `Honeyfield-Org/eurlex-mcp-server` (MIT, 2026-11-04), `Ansvar-Systems/comprehensive-eu-law-mcp` (Apache-2.0, a **pre-built DB, not live**).
- Clients: R `eurlex` package (CRAN, SPARQL-based); Python `eurlex` on PyPI (**unverified maintenance**).

---

## 2. Council of Europe: ECHR HUDOC. Tier A (undocumented), verified working 2026-11-05
- **Search** (JSON): `GET https://hudoc.echr.coe.int/app/query/results?query=...&select=...&sort=...&start=0&length=N`
  - Worked: `query=contentsitename:ECHR AND (NOT (doctype=PR OR doctype=HFCOMOLD OR doctype=HECOMOLD)) AND ("surveillance") AND ((documentcollectionid="GRANDCHAMBER"))`, `select=itemid,docname,appno,kpdate,doctype`, `sort=kpdate Descending`, `length=3` → `{"resultcount":300,"results":[{"columns":{"itemid":"001-252214","docname":"CASE OF KAVALA v. TÜRKİYE (No. 2)",...}}]}` ✔
  - Full-text keyword search: **yes** (bare quoted term in `query`). Useful fields: `itemid, appno, docname, kpdate, doctype (HEJUD=EN judgment, HFJUD=FR), importance, conclusion, article, respondent, ecli, languageisocode, documentcollectionid`.
- **Document**: `GET https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=001-210077` → 200, HTML fragment (≈930 KB including inline CSS) ✔. Strip the `<style>` block. PDF: `/app/conversion/pdf/?library=ECHR&id=...&filename=x.pdf` (**unverified**).
- Coverage: ECtHR 1959→today (judgments, decisions, communicated cases), former Commission, Committee of Ministers resolutions. Languages: EN/FR official, plus translations in other languages.
- Auth: none. Rate limits: none published. Terms: CoE copyright with free reuse for non-commercial and informational purposes (**unverified wording**). `robots.txt` returns the SPA HTML (no real robots file). The API is the one the official SPA uses and is undocumented, so it could change without notice.
- Existing: `pawelknorps/echr-mcp` (no licence file, pushed 2026-10-19), `pipeworx-io/mcp-hudoc` (MIT, 2026-11-02, 0★), `sitekwb/echr-mcp`. Python `echr-extractor` / `UlmApi/echr-scraping` exist (**unverified quality**).

---

## 3. Germany

### Case law + legislation: NeuRIS "Rechtsinformationsportal des Bundes" API. Tier A, verified working 2026-11-05
- Base `https://testphase.rechtsinformationen.bund.de`. Docs: `https://docs.rechtsinformationen.bund.de`, OpenAPI JSON at `https://docs.rechtsinformationen.bund.de/v3/api-docs` ✔. Source: `github.com/digitalservicebund/ris-search`. It is run by DigitalService GmbH for the federal Ministry of Justice (BMJV), and the docs label it a **trial service** ("may be subject to changes").
- `GET /v1/statistics` → `{"legislation":{"count":5518},"case-law":{"count":84784}}` ✔
- Courts (`/v1/rechtsprechung/courts`): BGH 35,609 · BFH 11,739 · BVerwG 10,461 · BPatG 7,347 · BAG 7,312 · BSG 6,505 · BVerfG 5,811. **Federal courts only; no Land courts.** Newest decision: BGH 28 Oct 2026.
- **Case law search** (full-text): `GET /v1/rechtsprechung?searchTerm=Mietminderung&size=1` → 158 hits, BGH VIII ZR 198/15 with ECLI ✔. Filters: `fileNumber, ecli, court, legalEffect, type, dateFrom, dateTo, sort, pageIndex`. Lucene syntax: `/v1/document/lucene-search/case-law?query=...`.
- **Decision text**: `/v1/rechtsprechung/KORE303742016.html` ✔ (also `.xml` LegalDocML, `.zip`). The HTML includes cited norms and the prior-instance chain.
- **Legislation search**: `GET /v1/legislation?searchTerm=Mietvertrag&size=1` ✔. Filters: `eli, abbreviation, temporalCoverageFrom/To, mostRelevantOn, dateFrom/To`. Results carry the ELI expression `eli/bund/bgbl-1/{year}/{num}/{pointInTime}/{version}/deu` and `legislationLegalForce: InForce`.
- **Per-article**: `/v1/legislation/eli/{jur}/{agent}/{year}/{natId}/{pit}/{ver}/{lang}/{pitManif}/{subtype}/{articleEid}.html` is in the OpenAPI spec. I did not exercise it.
- Rate limit: **600 req/min per IP** (503 above that), from the docs ✔. `robots.txt` = `Disallow: /`; this targets crawlers, and the API is explicitly meant for apps.
- **Gotchas (verified):**
  - `/v1/case-law` now returns **410 Gone** → use `/v1/rechtsprechung`. Legislation stays under `/v1/legislation`. `/v1/gesetze` returns 404.
  - **Legislation is incomplete:** `abbreviation=BGB`, `abbreviation=StGB` and `risAbbreviation=BGB` all returned **0 hits**, and the Grundgesetz itself was not in the top results. The docs say "The dataset is not yet complete." Don't rely on NeuRIS for core codes yet.
  - `searchTerm=Kündigung` returned 400 (non-ASCII in the URL). Percent-encode UTF-8 properly (`B%C3%BCrgerliches` worked).
- Licence: German statutes and judgments are public-domain official works (§ 5 UrhG). Explicit API terms: **unverified**.

### Legislation: gesetze-im-internet.de (GII). Tier A (static files), verified working 2026-11-05
- TOC: `https://www.gesetze-im-internet.de/gii-toc.xml` → 6,143 `<item>`s, each linking to `/{abbr}/xml.zip` ✔
- Whole law XML (consolidated, current only): `https://www.gesetze-im-internet.de/bgb/xml.zip` → 467 KB zip ✔
- Per-§ HTML: `https://www.gesetze-im-internet.de/bgb/__535.html` ✔ (ISO-8859-1). Article-level access is easy.
- No search API: build a local index over TOC titles, or use NeuRIS search. Identifier: GII slug (`bgb`, `stgb`, `gg`). No ELI here. No history, current version only.

### Case law: rechtsprechung-im-internet.de (federal courts, legacy)
- `https://www.rechtsprechung-im-internet.de/rii-toc.xml` → 23.5 MB, 84,835 items (court, date, Aktenzeichen, zip link) ✔. That is the same corpus as NeuRIS. A guessed `jportal/docs/bsjrs/KORE….zip` path returned 404; use the links in the TOC. NeuRIS supersedes it.

### Case law: Land courts. No official API
- **Open Legal Data** (third party, non-profit): `GET https://de.openlegaldata.io/api/cases/search/?text=Mietminderung&format=json` → 863 hits with highlighted snippets ✔. `/api/cases/?page_size=1` → count 425,210 ✔. `/api/cases/{id}/` ✔. Reads worked **without an API key**. Covers OLG/LG/AG/VG plus federal courts and EuGH. Licence/ToS: **unverified** (ODbL for the DB is likely). Not official, and coverage is patchy.
- Per-Land portals (e.g. `landesrecht-bw.de`, `gesetze-bayern.de`, NRW `justiz.nrw.de/nrwe`): HTML or juris-backed. **Unverified**; not tested.

### Existing MCP / clients
- `wolfgangihloff/rechtsinformationen-bund-de-mcp` (★24, no licence, pushed 2026-06-26): NeuRIS.
- `JustiziusAI/german-law-mcp` (MIT, NeuRIS), `timothyc012/german-law-mcp` (MIT), `Ansvar-Systems/German-law-mcp` (Apache-2.0, GII, pre-built DB), `kaibruell/gesetze-im-internet-mcp` (MIT).
- `82rrj28rb8-dev/openlegaldata-mcp`. Python: `5drei1/neuris-python`; `tech4germany/rechtsinfo_api` (older GII-based API).

---

## 4. Austria: RIS OGD API v2.6. Tier A, verified working 2026-11-05
- Base `https://data.bka.gv.at/ris/api/v2.6/` with `Judikatur`, `Bundesrecht`, `Landesrecht`, `Bezirke`, `Gemeinden`, `Sonstige` (REST/JSON; XML also offered). No auth. Licence: **CC BY 4.0** (Austrian OGD; attribution "Quelle: RIS"). Rate limit: none published (**unverified**).
- **Case law, full-text**: `GET .../Judikatur?Applikation=Justiz&Suchworte=Mietzinsminderung&DokumenteProSeite=Ten` → 38 hits (OGH Rechtssätze + decisions) ✔. `Applikation=Vfgh&Suchworte=Datenschutz` → 417 ✔. Other Applikationen: `Vwgh`, `Bvwg`, `Lvwg`, `Dsk`, `Normenliste` and more. OGH from ~1950s (Rechtssätze), with substantial coverage from the 1990s.
- **Legislation**, consolidated, **per-paragraph documents** (one `NOR…` id per §):
  - `.../Bundesrecht?Applikation=BrKons&Gesetzesnummer=10001622&Abschnitt.Von=1090&Abschnitt.Bis=1090&Abschnitt.Typ=Paragraph` → exactly 1 hit: ABGB § 1090 = `NOR12018819` ✔
  - `Titel=ABGB` alone → 2,570 hits, one per §. The `Paragraph.Von` param is **silently ignored**; use `Abschnitt.*`.
  - Content: `https://ogd.ris.bka.gv.at/Dokumente/Bundesnormen/NOR12017691/NOR12017691.xml` → 200 ✔ (also `.html`, `.rtf`, `.pdf`). Each result's `Dokumentliste.ContentReference.Urls` gives the URLs.
  - Landesrecht: `.../Landesrecht?Applikation=LrKons&Bundesland.SucheInWien=true&Suchworte=Bauordnung` → 1,031 ✔
- Identifiers: Gesetzesnummer (e.g. ABGB 10001622), NOR document ids, **ELI** (`/eli/jgs/1811/946/P1/NOR12017691`), ECLI for case law (`data.bka.gv.at/ecli/` sitemaps).
- **Gotchas:** `https://www.ris.bka.gv.at/Dokumente/...` returned **503 "Security Check"**, while the `ogd.ris.bka.gv.at` host works. `data.bka.gv.at/robots.txt` is `Disallow: /`, but the API is the documented OGD interface. Single results come back as an object, not a list, so normalise.
- Existing MCP: `cyanheads/ris-austria-mcp-server` (Apache-2.0, pushed 2026-10-31; federal + state law, decisions, BGBl). `Ansvar-Systems/Austrian-law-mcp` (Apache-2.0, DB-based). The R package `ris` / Python wrappers exist (**unverified**).

---

## 5. Switzerland

### Case law: entscheidsuche.ch (non-profit association, all Swiss courts). Tier A, verified working 2026-11-05
- Elasticsearch passthrough: `POST https://entscheidsuche.ch/_search.php` with an ES JSON body, e.g. `{"query":{"simple_query_string":{"query":"Mietzinsherabsetzung","default_operator":"and"}},"size":2,"_source":["id","date","canton","title","url","hierarchy"]}` → 295 hits ✔. `_source.attachment.content` holds the **full text**, and `attachment.content_url` points to `https://entscheidsuche.ch/docs/{Spider}/{id}.html|.pdf|.json`.
- Static files: `https://entscheidsuche.ch/docs/BS_Omni/BS_APG_001_BEZ-2013-54_2014-03-31.{html,json}` ✔ (directory listings are open).
- Coverage: BGer/BGE, BVGer, BStGer, BPatGer, all 26 cantons, some authorities. Languages: DE/FR/IT. `robots.txt` = `Allow: /`. Licence: "open data" per the association. Exact licence **unverified**.
- **Already has an MCP:** `https://mcp.entscheidsuche.ch/mcp` (Streamable HTTP, no auth). `initialize` returned `serverInfo {"name":"entscheidsuche","version":"1.27.0"}` ✔. Code: `github.com/entscheidsuche/entscheidsuche-mcp` (MIT). **Consider proxying or delegating to it instead of re-implementing.** Also `self-tech-labs/entscheidsuche-MCP-server`.

### Case law: Bundesgericht (bger.ch). Tier C, verified working 2026-11-05
- Full-text HTML search: `https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?lang=de&type=simple_query&query_words=Mietzins&top_subcollection_aza=all` → "1098 exakte Treffer" ✔ (ISO-8859-1). Document: `...index.php?lang=de&type=show_document&highlight_docid=aza://12-03-2024-4A_472-2023` → 200 ✔.
- `robots.txt`: `/ext/eurospider` is not disallowed (`/php/azabvger` and `/php/jurivoc` are). **`Crawl-delay: 2`**. Covers unpublished judgments from 2000 and BGE (leading cases, the `/clir/` collection, **unverified**). entscheidsuche already mirrors all of this, so prefer it.

### Legislation: Fedlex. Tier A, verified working 2026-11-05
- SPARQL: `GET https://fedlex.data.admin.ch/sparqlendpoint?query=...` with `Accept: application/sparql-results+json` (JOLux ontology, the same family as Legilux). Title search on `jolux:ConsolidationAbstract` / `jolux:isRealizedBy` / `jolux:title` with `FILTER(CONTAINS(?title,"Obligationenrecht"))` → `https://fedlex.data.admin.ch/eli/cc/27/317_321_377` (OR, SR 220) ✔.
- Consolidated text (**Akoma Ntoso XML**): `https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/27/317_321_377/20260101/de/xml/fedlex-data-admin-ch-eli-cc-27-317_321_377-20260101-de-xml-1.xml` → 200, 2.4 MB ✔. Also HTML/PDF/DOCX. Resolve the latest consolidation date and file URLs through SPARQL (`jolux:isMemberOf`, `jolux:dateApplicability`, `jolux:isEmbodiedBy`, `jolux:isExemplifiedBy`) rather than guessing the date.
- Identifiers: **ELI** `eli/cc/{AS-year}/{num}` (cc = consolidated "classified compilation"), plus the SR number (e.g. 220). Per-article: whole document only, so slice AKN `<article eId="art_253">` locally. Languages: DE/FR/IT (RM and EN for some).
- `www.fedlex.admin.ch` is an Angular SPA (no server-side text), so use the filestore. `robots.txt`: Allow `/`.
- Existing MCP: `malkreide/fedlex-mcp` (MIT, 2026-11-01), `JayTheSkier/fedlex-connector` (MIT), `mindful-bio/mcp-fedlex` (Apache-2.0), `loicvuilliomenet-boop/fedlex-mcp`. Data mirror: `droid-f/fedlex`. Ontology docs: `swiss/fedlex-jolux`.

---

## 6. France

### Case law: Judilibre (Cour de cassation, plus cours d'appel and tribunaux judiciaires being rolled out). Tier B
- `https://api.piste.gouv.fr/cassation/judilibre/v1.0/{search,decision,export,scan,taxonomy,healthcheck}`. Sandbox: `sandbox-api.piste.gouv.fr`.
- Without a token → **400 `WWW-Authenticate: Bearer … "Unable to find token in the message"`**. With a fake token → 401 ✔. Auth is a **free PISTE account → create an app → subscribe to the Judilibre API + accept its CGU → OAuth2 client_credentials** (`https://oauth.piste.gouv.fr/api/oauth/token`). Authenticated calls: **unverified** (no credentials).
- Full-text search: yes (`/search?query=...`, filters by jurisdiction/chamber/date/solution). Licence: Licence Ouverte / Etalab 2.0 (open-data of judgments, pseudonymised). Quotas: **unverified**.
- Source code is public: `github.com/Cour-de-cassation/judilibre-search`.
- `www.courdecassation.fr/recherche-judilibre` → JS + cookie redirect wall (`/redirect_…`), so HTML scraping is impractical.

### Case law: administrative courts (Conseil d'État, CAA, TA)
- `https://opendata.justice-administrative.fr/`: bulk XML dumps (200 ✔). There is no live search API. ArianeWeb (CE) is HTML only (**unverified**). Légifrance's PISTE API also exposes the JADE (administrative) and CAPP/INCA/JURI (judicial) funds.

### Legislation: Légifrance. Tier B
- `https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/` with `/search`, `/consult/code`, `/consult/getArticle`, `/consult/legiPart`, `/consult/jorf`, etc. The same PISTE OAuth flow → 400 without a token ✔.
- Consolidated text: yes (LEGI fund, with point-in-time versions). **Per-article**: yes (`LEGIARTI…` ids). Identifiers: LEGITEXT/LEGIARTI/JORFTEXT, NOR, ELI (`/eli/loi/2016/10/7/…`).
- `www.legifrance.gouv.fr/codes/article_lc/LEGIARTI…` → **Cloudflare 403 "Just a moment…"** ✔. HTML is not usable.
- Bulk alternative (no key): DILA dumps `https://echanges.dila.gouv.fr/OPENDATA/LEGI/` (200 ✔), also JORF, KALI, CASS, JADE. Licence Ouverte 2.0. They are not live, but usable for an ID→title index.
- Existing MCP: **`pylegifrance/mcp-server-legifrance`** (MIT, ★65, 2026-10-05), **`jmtanguy/droit-francais-mcp`** (MIT, ★36, Légifrance + Judilibre, 2026-10-27), `sancelot/legifrance-mcpserver`, `nitrique/legifrance-mcp`, several Judilibre MCPs (0★). Clients: `pylegifrance` (PyPI), `pauldechorgnat/pyJudilibre` (MIT). French is the most saturated jurisdiction in this region for MCPs.

---

## 7. Belgium

### Case law: Juportal (SPF Justice). Tier C/D
- Decision page: `https://juportal.be/content/ECLI:BE:CASS:2017:ARR.20170502.1/FR` (or `/NL`) → 200 ✔, with summary, keywords and full text. The canonical form is `https://juportal.just.fgov.be/content/ViewDecision.php?id={ECLI}&lang=fr`. A wrong ECLI returns 404 "NOT FOUND".
- Discovery: **daily ECLI sitemaps**: `https://juportal.just.fgov.be/JUPORTAsitemap/2026/11/04/sitemap_index_1.xml` ✔. These are EU ECLI-format entries with court, date, language and text URLs. Good for an "updates since date" tool.
- Search: an HTML form (POST) only, with no API (**unverified** details).
- **`juportal.be/robots.txt`: `User-agent: * Disallow: /`; only `DG_JUSTICE_CRAWLER` is allowed.** Automated access goes against robots.txt, so treat it as tier **D** unless permission is obtained. Coverage: Cassation and the Constitutional/Council of State courts in part; lower courts are sparse. Languages: FR/NL/DE.
- Constitutional Court (`const-court.be`) and Council of State (`raadvst-consetat.be`) have their own HTML sites. **Unverified**.

### Legislation: Justel / Moniteur belge (eJustice). Tier C/D
- Consolidated law by ELI: `https://www.ejustice.just.fgov.be/eli/loi/1804/03/21/1804032150/justel` (Code civil) → 200, 1.15 MB HTML (ISO-8859-1) with articles ✔. Whole document only, so split by `Art. N` locally.
- **`ejustice.just.fgov.be/robots.txt` disallows `/eli/`, `/cgi_loi/`, `/loi/`, `/wet/`, `/mopdf/`**, and that covers every useful path. HTML only, with no API.
- Identifiers: ELI (`eli/{type}/{yyyy}/{mm}/{dd}/{numac}/justel`), NUMAC.
- Existing: `Ansvar-Systems/Belgian-law-mcp` (Apache-2.0; **pre-built DB of 5,775 acts in French**, not live; the DB itself is not distributed because of TDM constraints). Others: `rafjaf/BetterJustel` (GPL-3, browser extension), `Fedict/justel2book`.

---

## 8. Luxembourg

### Legislation: Legilux. Tier A (SPARQL + filestore), verified working 2026-11-05
- SPARQL: `GET https://data.legilux.public.lu/sparqlendpoint?query=...` with `Accept: application/sparql-results+json` or `text/csv` (**JOLux** ontology, the same as fedlex).
  - Title search: `?act jolux:isRealizedBy ?e . ?e jolux:title ?title . FILTER(CONTAINS(LCASE(?title),"code civil"))` ✔
  - Latest consolidation: `?c jolux:isMemberOf <http://data.legilux.public.lu/eli/etat/leg/loi/1804/03/21/n1> ; a jolux:Consolidation ; jolux:dateApplicability ?d } ORDER BY DESC(?d)` → `…/eli/etat/leg/code/civil/20251226` ✔
  - File URLs: `?e jolux:isEmbodiedBy ?m . ?m jolux:isExemplifiedBy ?f` → html/pdf/xml/docx ✔
- Consolidated **Akoma Ntoso XML**: `https://data.legilux.public.lu/filestore/eli/etat/leg/code/civil/20251226/fr/xml/eli-etat-leg-code-civil-20251226-fr-xml.xml` → 200, 5.4 MB ✔. Whole document, so slice articles locally.
- `legilux.public.lu/eli/...` HTML is an SPA shell (2 KB), so use the filestore.
- Identifier: **ELI** (`eli/etat/leg/{type}/{yyyy}/{mm}/{dd}/{n}/jo`; consolidations `eli/etat/leg/code/civil/{yyyymmdd}`). Language: FR.
- Licence: data.public.lu dataset "Legilux – Journal officiel" = **CC-BY** ✔. `data.legilux.public.lu/robots.txt` has `Disallow: /eli/*` and `Disallow: /filestore/*`, which conflicts with that open-data licence. Low-volume on-demand fetches are defensible, but **note this.**
- Existing: `Ansvar-Systems/Luxembourg-law-mcp` (Apache-2.0, DB of 4,551 acts), `SFHAJJI/lex-corpus-lu-legilux` (CC-BY-4.0 full corpus mirror), `sparna-git/sparnatural-legilux-casemates`.

### Case law. Tier D for live search
- `justice.public.lu/fr/jurisprudence/...` → redirected to **`challenge.html` (FriendlyCaptcha)** ✔. `ja.public.lu` (administrative courts) → **403** ✔.
- Bulk only: data.public.lu organisation "Administration judiciaire" has **97 datasets**, e.g. `cour-de-cassation-1` (48 resources, yearly ZIPs, latest `2026.zip` updated 2026-11-02) plus per-chamber Tribunal d'arrondissement datasets. Licence **CC BY-ND** ✔. API: `https://data.public.lu/api/1/datasets/cour-de-cassation-1/` ✔. A "live" tool would have to download and grep yearly ZIPs. That is feasible for Cassation (small), but there is no search.

---

## Cross-cutting gotchas
1. **Bot walls are now the main blocker, not auth:** EUR-Lex (AWS WAF), Légifrance (Cloudflare), courdecassation.fr (JS redirect), justice.public.lu (FriendlyCaptcha), RIS www host (Security Check). In each case the official data host (CELLAR, PISTE, ogd.ris, data.legilux) works.
2. **Two SPA migrations broke old scrapers:** CURIA → InfoCuria, and fedlex.admin.ch. Old `curia.europa.eu/juris/liste.jsf` scrapers are dead.
3. **JOLux is shared** by fedlex (CH) and Legilux (LU), so one SPARQL adapter can serve both. CELLAR uses CDM, which is a different ontology but the same Virtuoso/SPARQL pattern.
4. **Akoma Ntoso** is used by fedlex, Legilux and NeuRIS (LegalDocML.de), so one AKN parser covers 3 jurisdictions.
5. `robots.txt` says `Disallow: /` on several *official APIs* (NeuRIS, data.bka.gv.at) that are explicitly for programmatic use. That is fine. It is different for Belgium (Juportal, Justel), where the disallow targets the content pages themselves.
6. Existing MCP saturation: FR (many), CH-case-law (official MCP), EU (cyanheads, good), AT (cyanheads), DE-NeuRIS (several). **The gaps are a combined DE (NeuRIS case law + GII statutes) server, LU, BE, and a multi-jurisdiction façade.**
