# MENA, Sub-Saharan Africa & International Courts — open legal data sources

Research date: **2026-11-05**. Probed from a UK IP with a Chrome User-Agent, read-only GETs, a few requests per source.
"verified" = I made the request and saw the result on 2026-11-05. "unverified" = from docs, source code or memory, not confirmed live.
Tiers: **A** = official API, no key · **B** = official API, free key · **C** = HTML only (or an undocumented JSON the site's own frontend uses), automated access allowed · **D** = paid, forbidden, nothing usable, geo-blocked or bot-walled.

## Summary table

| Jurisdiction / body | Case law | Legislation | Best endpoint | Auth | Notes |
|---|---|---|---|---|---|
| **Peachjam LII network (17 sites)** | C (search) / D (docs) | C / D | `https://{lii}/search/api/documents/?search=…` | none | Search JSON verified on 17 sites. Document pages are behind a Cloudflare/AWS-WAF JS challenge on most of them. robots.txt says `ai-input=no` and blocks ClaudeBot. |
| Laws.Africa Content / KB API | B (tiny free tier) / D | B / D | `api.laws.africa/ai/v1/knowledge-bases/{code}/retrieve` | Bearer token | Free Sandbox = 1 country, 100 calls/day. Full Content API is commercial (from R500k per country per year). |
| South Africa | D (SAFLII) / C-D (lawlibrary.org.za) | C (gov.za PDFs) / D | lawlibrary.org.za search API | none | SAFLII is behind a Cloudflare challenge (403). |
| Kenya | C search / D docs | C search / D docs | kenyalaw.org search API | none (API by email) | ToU bans scraping and bots. AWS WAF challenge on docs. An existing MCP exists. |
| Nigeria | **C (search + docs both work)** | D (none on NigeriaLII) | nigerialii.org | none | The only LII tested whose document pages were not challenged. Judgments only. |
| Ghana | C search / D docs | C (listing pages load) / D | ghalii.org | none | |
| Uganda, Zambia, Zimbabwe, Malawi, Namibia, Tanzania, Zanzibar, Lesotho, Eswatini, Sierra Leone, Rwanda, Mauritius | C search / D docs | same | `{lii}/search/api/documents/` | none | Same Peachjam codebase as above. |
| Seychelles (SeyLII) | D | D | — | — | No longer on Peachjam (Spring Boot 404 JSON). |
| Israel | D (court sites reset / 403 from UK) | **A-ish**: Knesset OData (metadata + gazette PDFs) + Hebrew Wikisource Open Law Book (consolidated text, MediaWiki API) | `knesset.gov.il/Odata/ParliamentInfo.svc/KNS_IsraelLaw()` | none | Nevo/Takdin are paid. Wikisource is crowd-sourced, CC BY-SA. 3+ Israeli MCPs exist. |
| UAE federal | — | D (uaelegislation.gov.ae: Cloudflare 403) | — | — | |
| UAE – DIFC Courts | **C** (open HTML, robots allows) | C (DIFC laws, unverified) | `difccourts.ae/rules-decisions/judgments-orders` | none | English common law. Full text is in HTML. |
| UAE – ADGM Courts | C (HTML list → sealed PDFs) | C (unverified) | `adgm.com/adgm-courts/judgments` | none | robots disallows `/api/`. |
| Saudi Arabia | C/D (MoJ portal SPA with undocumented gateway) | D from UK (laws.boe.gov.sa timed out) | `laws-gateway.moj.gov.sa/apis/legislations/v1` (unverified) | unknown | Geo/WAF issues. |
| Qatar | D/unverified | C/unverified (Al Meezan is a React SPA) | almeezan.qa | — | QICDRC site loads (HTML). |
| Bahrain | — | C (legalaffairs.gov.bh MVC HTML) | `/Legislation/Search` | none | `www.` host has a bad TLS cert. Use the bare host. |
| Oman | — | C (qanoon.om, unofficial: WordPress REST works) | `qanoon.om/wp-json/wp/v2/posts?search=` | none | Not an official source. |
| Kuwait | D/unverified | D/unverified | moj.gov.kw (SharePoint) | — | |
| Jordan | D (Qistas is paid) | C/unverified (lob.gov.jo SPA) | lob.gov.jo | — | |
| Lebanon | C (rulings search, unverified) | **C** (legiliban.ul.edu.lb `Law.aspx?lawId=`) | legiliban.ul.edu.lb | none | Lebanese University legal informatics centre. |
| Egypt | D/C (cc.gov.eg Supreme Constitutional Court HTML) | D (no official free consolidated source) | cc.gov.eg | — | |
| Morocco | D (juriscassation.cspj.ma times out) | C (adala.justice.gov.ma PDFs, sgg.gov.ma BO) | adala.justice.gov.ma | none | |
| Tunisia | D (legislation.tn refuses connection) | D/C (iort.gov.tn JORT) | — | — | |
| Algeria | D (coursupreme.dz times out) | C (joradp.dz JO PDFs) | joradp.dz | none | |
| ICJ | C (HTML case pages, search) / D (PDFs behind Cloudflare challenge) | n/a | `icj-cij.org/case/{n}/judgments` | none | PDFs return 403 `cf-mitigated: challenge`. |
| ICC | D on icc-cpi.int (Gcore JS wall) → **use Legal Tools DB** | n/a | `legal-tools.org/api/ltddocs?filter=…` (LoopBack JSON, 441,310 docs) | none | Undocumented API. robots says `use=reference`, ai-train=no, blocks ClaudeBot. |
| ITLOS | **C** (HTML + direct PDFs work) | n/a | `itlos.org/en/main/cases/list-of-cases/` | none | robots disallows its own ke-search. |
| PCA | D (pca-cpa.org and pcacases.com/web/view are Cloudflare-challenged) | n/a | — | — | |
| WTO disputes | C (wto.org `dsNNN_e.htm` pages) | n/a | `wto.org/english/tratop_e/dispu_e/cases_e/ds{n}_e.htm` | none | The WTO API portal (free key) has **no** dispute API. docs.wto.org robots `Disallow: /`. |
| UN Treaty Collection | n/a | **C** (HTML, `Crawl-delay: 2`) | `treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=…` | none | Status pages are large (1.3 MB). |
| ICSID | **C+ (undocumented JSON)** | n/a | `icsid.worldbank.org/api/all/cases` (1.6 MB JSON of all cases + decision links) | none | italaw is behind a Cloudflare challenge. |
| Inter-American Court HR | D (corteidh.or.cr Cloudflare challenge; search is a vLex-hosted SPA) | n/a | — | — | |
| African Court HPR | C (african-court.org HTML) + Peachjam search via africanlii (`/akn/aa-au/judgment/afchpr/…`) | n/a | africanlii.org search API | none | |
| EFTA Court | **C+ (undocumented JSON)** | n/a | `api.eftacourt.int/api/cases`, `/api/cases/{id}` | none | 463 cases. Document text endpoint not found. |
| EAEU Court | C (HTML loads, Bitrix) | n/a | courteurasian.org/court_cases/eaeu/ | none | Russian. |
| CIS Economic Court | D (sudsng.org timed out) | n/a | — | — | |
| ECOWAS Court | C (HTML loads) | n/a | courtecowas.org | none | Also check africanlii. |
| EACJ | D from UK (eacj.org timed out) | n/a | via africanlii (unverified) | — | |

**Bottom line:** there is no tier-A case-law source anywhere in this region. The best pieces are:
- the Peachjam search JSON, which works on 17 sites but whose full text is bot-walled;
- the EFTA, ICSID and Legal Tools undocumented JSON APIs;
- Knesset OData plus Hebrew Wikisource for Israeli legislation;
- DIFC, ITLOS and NigeriaLII, where plain HTML works.

---

## 1. Peachjam / LII platform (Laws.Africa) — can one adapter cover 15+ countries?

**Short answer:** for **search, yes, verified on 17 sites**. For **reading the document, no**: most sites now put the `/akn/...` document pages behind a bot challenge. Their robots.txt also explicitly withholds consent for `ai-input`, which is exactly the MCP use case.

### Platform
- **Code:** `github.com/laws-africa/peachjam` (GPL-3.0, Django + Elasticsearch, pushed 2026-11-05, so actively maintained). Site apps in the repo: liiweb (generic), eswatinilii, lesotholii, malawilii, mauritiuslii, nigerialii, rwandalii, seylii, sierralii, tcilii, zambialii, zanzibarlii, zimlii. Kenya Law also runs Peachjam: identical JSON and templates.
- **Identifiers:** Akoma Ntoso FRBR URIs, the same on every site:
  - judgment: `/akn/{cc}/judgment/{court}/{year}/{num}/{lang}@{date}`, e.g. `/akn/ke/judgment/kehc/2026/11803/eng@2026-07-28`
  - act: `/akn/{cc}/act/{year}/{num}/{lang}@{expr-date}`, e.g. `/akn/mw/act/1994/20/eng@2020-11-03`
  - subsidiary legislation: `/akn/zm/act/si/2015/74/eng@…`
  - regional/AU: `/akn/aa-au/judgment/afchpr/2023/16/eng@2023-06-13`
  - `{cc}-{locality}` for by-laws.
- **Original file:** `{FRBR}/source` (PDF or DOCX).

### Search endpoint (verified working 2026-11-05)
```
GET https://{site}/search/api/documents/?search=<text>[&doc_type=judgment|legislation|gazette|book|generic_document]
    [&court=<court name, exact facet value>][&judges=…][&year=…][&date=…][&language=…][&jurisdiction=…]
    [&ordering=-score|date|-date][&page=1..10][&mode=text|semantic|hybrid]
GET https://{site}/search/api/documents/facets?search=<text>   → ES aggregations (doc_type, court, year, judges, …)
```
- **Response:** JSON `{count, facets, results_html, flynote_results_html, entity_results_html, trace_id, can_semantic}`. Results are **HTML fragments**. Parse `<li class="hit" data-document-id>`, `a[data-frbr-uri]` (title + citation), the date and court `<span>`s, and `.snippet` (it contains `<mark>` highlights).
- **Paging:** 10 hits per page, **max page=10**, so 100 hits per query. `page=11` returns 400 `{"error":{"page":["Ensure this value is less than or equal to 10."]}}`.
- **Filter values are lowercase facet keys**: `doc_type=judgment` works, `Judgment` returns 0. Court filter uses the display name, e.g. `court=Supreme+Court+of+Zambia` (verified: 23 hits).
- **Language prefix:** some hosts redirect to it: `ulii.org/en/…`, `africanlii.org/en/…`, `namiblii.org/en/…`, `tanzlii.org/en/…`, `zanzibarlii.org/sw/…` (302). Follow redirects, or hard-code the prefix.
- **Full-text keyword search:** yes. Boolean and phrase support follows ES `simple_query_string` semantics (unverified detail). `mode=semantic` exists on Kenya Law (verified: it returns results).
- **Rate limits:** not published. Responses are CloudFront-cached (`cache-control: max-age=900`).

**Sites verified 2026-11-05** (search count for `constitution` or similar):

| Site | Country | Count |
|---|---|---|
| kenyalaw.org | KE | 10000+ |
| lawlibrary.org.za | ZA | 10000+ |
| africanlii.org/en | AU + regional courts | 10000+ |
| tanzlii.org/en | TZ | 10000+ |
| ghalii.org | GH | 8963 |
| zimlii.org | ZW | 7281 |
| namiblii.org/en | NA | 6893 |
| eswatinilii.org | SZ | 3185 |
| malawilii.org | MW | 2576 |
| rwandalii.org | RW | 2345 |
| lesotholii.org | LS | 1973 |
| zanzibarlii.org/sw | Zanzibar | 1348 |
| nigerialii.org | NG, judgments only | 948 |
| sierralii.gov.sl | SL | 549 |
| mauritiuslii.org | MU | 398 |
| ulii.org/en | UG | 8272 for "land use" |
| zambialii.org | ZM | 125 for "land tenure" |

That is **17 working sites, 16 countries + AU/regional**.

**Not working:**
- seylii.org (migrated off Peachjam).
- gambialii.gm, liberialii.org, liberlii.org: no connect / 403.
- saflii.org: Cloudflare challenge, and it is AustLII-style, not Peachjam.

### Document fetch — the blocker (verified 2026-11-05)
`GET https://{site}/akn/…` returned:

| Site(s) | Result |
|---|---|
| zambialii, ghalii, lawlibrary.org.za, zimlii, malawilii, ulii, africanlii | **403 `cf-mitigated: challenge`** ("Just a moment… Enable JavaScript") |
| kenyalaw.org | **202 `x-amzn-waf-action: challenge`**, empty body |
| nigerialii.org | **200** with full text in `<div class="content content__html" id="document_content">`. Judgment text extracted fine. |

- Listing pages are also challenged on some sites (e.g. `lawlibrary.org.za/judgments/ZACC/` → 403), but not all (`ghalii.org/legislation/` → 200).
- The search API itself was **not** challenged.
- Legislation pages use Indigo/law-widgets AKN HTML with stable ids per provision (`sec_1`, `chp_2`, …), so per-section extraction is possible when reachable. That id detail is unverified live, because every legislation page I tried was challenged.

### Terms / robots (verified 2026-11-05) — read before building
- **robots.txt on every Peachjam site:** `Content-Signal: ai-train=no, search=yes, ai-input=no`, `Disallow: /api/`. africanlii and legal-tools add `use=reference` and explicitly `Disallow: /` for `ClaudeBot`, `anthropic-ai`, `Claude-Web`, GPTBot and others. The robots text defines **ai-input as "inputting content into one or more AI models (e.g. RAG, grounding, or other real-time taking of content for generative AI search answers)"**, which is literally what a live-fetch MCP does. It cites EU DSM Directive art. 4 as an express reservation of rights.
- **Kenya Law ToU** (`kenyalaw.org/terms-of-use/`): "Scraping, deployment of unauthorized bots and bulk downloading from this website is strictly prohibited… access the data through our APIs. Please email us if you would like to access our API." Kenya Law therefore has a non-public API available on request: tier B/D, unverified.
- **Conclusion:** a generic Peachjam adapter is technically trivial for search. Fetching full text, however, means circumventing bot challenges against stated reservations. **Treat Peachjam doc fetch as tier D** unless Laws.Africa grants access. The only clean path for those sites is "search + link out", or the paid/limited Laws.Africa API.

### Laws.Africa API (verified 2026-11-05)
- `GET https://api.laws.africa/v3/` → 403 `{"detail":"Authentication credentials were not provided."}`. Also `/v2/`, and `{site}/api/` on Peachjam sites.
- **Knowledge Bases (RAG retrieval):** `POST https://api.laws.africa/ai/v1/knowledge-bases/{code}/retrieve`, with `Authorization: Bearer <token>` from platform.laws.africa.
  - Judgment KBs return **summaries + metadata, not full judgment text**.
  - Plans (developers.laws.africa/get-started/pricing.md):

    | Plan | Price | Includes |
    |---|---|---|
    | **Sandbox** | free | 1 country, 100 calls/day |
    | Build | ZAR 4,200 per KB per month | 3,000 calls/day |
    | Scale | ZAR 6,700 per KB per country per month | 10,000/day |
- **Content API (full legislation, AKN XML, point-in-time):** the commercial page `laws.africa/platform/content/` gives:

  | Package | Price |
  |---|---|
  | Index | R500k per country/year |
  | Integrate | R1.5m |
  | Analyse (AKN XML) | R2m |
  | + History | R3m |

  It is sales-assisted. A free experimental scope exists for Cape Town by-laws only. The endpoint shape is `api.laws.africa/v3/akn/{cc}/act/{year}/{num}/{lang}/toc` and so on.
- Laws.Africa says it maintains collections in "six African jurisdictions". **Tier: B for a 1-country, 100/day sandbox; otherwise D (paid).**

### Existing code
- `Verantu-Labs/kenya-law-mcp`: MIT, TypeScript/Bun, pushed 2026-10-16, 1★. Tools: search_case_law, search_legislation, get_akn_document. A hosted worker exists. Given the WAF findings, how it fetches documents should be checked.
- `OxfordIHTM/africalaws`: GPL-3.0, R client for the Laws.Africa API (2025-08).
- `africanlii/liiweb`: old Drupal LII, archived 2023.

---

## 2. South Africa
- **Case law:**
  - **SAFLII** (`saflii.org`): AustLII-style static HTML, `/za/cases/ZACC/2024/1.html`. **403 `cf-mitigated: challenge`** (verified), and the robots content-signal reservations apply. Tier D.
  - **lawlibrary.org.za** (Laws.Africa Peachjam): search API works (`unfair dismissal` + `doc_type=judgment` gives 4490 hits, e.g. `/akn/za/judgment/zalcpe/2014/23/eng@2014-05-16`). Docs are challenged. Tier C (search) / D (text).
  - Constitutional Court `concourt.org.za` loads (200, HTML). Judgment links point to SAFLII/Collections (unverified).
- **Legislation:**
  - `gov.za/documents/acts`: 200, HTML listings + as-enacted PDFs, not consolidated. Tier C.
  - Consolidated text is only on lawlibrary.org.za (challenged) or the paid Laws.Africa API.
- **Languages:** English (plus Afrikaans/others for some Acts).

## 3. Kenya
- **Case law + legislation:** `kenyalaw.org` (NCLR) is Peachjam. Search verified (`breach of contract` → 10000+). Document pages are AWS-WAF-challenged.
- Laws of Kenya are consolidated and AKN-structured (`/akn/ke/act/2010/constitution/…`).
- The ToU forbids bots and scraping but offers an **API on email request** (info@kenyalaw.org). Tier C (search) / D (text), possibly B by agreement.
- The Kenya Law MCP above exists.

## 4. Nigeria
- **Case law:** `nigerialii.org` (Peachjam). Search verified. **Document pages returned 200 with full text** (e.g. `/akn/ng/judgment/ngsc/1993/3/eng@1993-03-05`, Akintola v Oyelade, SC 129/1988). Facets show **only judgments** (1349 hits for "act"), mainly the Supreme Court. Tier C, but the same robots `ai-input=no` reservation applies.
- **Legislation:** there is no official free consolidated source. NigeriaLII had zero legislation. Tier D. The paid alternatives are LawPavilion and Nigeria-Law.org (not checked).

## 5. Ghana
- **Case law:** `ghalii.org`. Search verified (`fundamental human rights` + judgment gives 2708 hits). Doc pages are challenged. Tier C/D.
- **Legislation:** `ghalii.org/legislation/` listing loads (200). Act pages are likely challenged. Tier C/D.

## 6. Other Sub-Saharan LIIs
Uganda (ulii), Zambia, Zimbabwe, Malawi, Namibia, Tanzania, Zanzibar, Lesotho, Eswatini, Sierra Leone, Rwanda and Mauritius all behave identically: search works, docs are challenged, robots carries `ai-input=no`. Seychelles (seylii) left Peachjam: `/search/api/documents/` → Spring-style 404 JSON. The Gambia and Liberia LIIs were unreachable.

---

## 7. Israel
- **Case law:**
  - `supreme.court.gov.il` → 200 (SharePoint HTML).
  - `supremedecisions.court.gov.il` and `elyon1.court.gov.il` → **connection reset** from the UK.
  - `gov.il` → 403.
  - Nevo and Takdin are paid.
  - Tier D from outside Israel. Could be C from an Israeli IP (unverified).
- **Legislation:**
  - **Knesset OData v3** (verified, no auth): `https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_IsraelLaw()?$filter=substringof('חוזים',Name)&$format=json&$top=3` returns `IsraelLawID` 2000292 "חוק החוזים (חלק כללי), התשל"ג-1973", status תקף. Other tables: `KNS_IsraelLawName`, `KNS_DocumentLaw` (→ Reshumot gazette PDFs at `fs.knesset.gov.il/…/law/…_lsr_….pdf`), `KNS_Bill`, `KNS_LawBinding` (amendment links). This is metadata + as-published PDFs, **not consolidated text**. Tier A (metadata).
  - **Open Law Book (ספר החוקים הפתוח), Hebrew Wikisource** (verified): `https://he.wikisource.org/w/api.php?action=parse&page=חוק החוזים (חלק כללי)&prop=wikitext&format=json` returns consolidated wikitext (18,952 chars) up to amendment no. 3 of 5786, with `{{ח:מאגר|2000292}}` linking to the Knesset ID. Section templates `{{ח:סעיף|…}}` allow per-section parsing. Search: `list=search&srsearch=…`. Licence CC BY-SA. Crowd-maintained, so not official. Tier A (open API), with a caveat on authority.
- **Existing MCPs:**
  - `JohnJackHouzi/mishpat-israel` (MIT, 2026-10-23: Open Law Book + Reshumot + Knesset)
  - `matematicsolutions/il-eli-mcp` (Apache-2.0, 2026-10-06, Knesset OData)
  - `kaerez/israel-law-mcp` / `PointStarIL/israel-law-mcp` (custom licence, topic-limited)
  - `dani-yakir/knesset-utils`

## 8. UAE
- **Federal legislation:** `uaelegislation.gov.ae` → **403 Cloudflare** (verified on `/en` and `/en/legislations`). `elaws.moj.gov.ae` timed out. Tier D from here.
- **DIFC Courts** (English, common law): `https://www.difccourts.ae/rules-decisions/judgments-orders`.
  - 200. Concrete CMS listing with paging `?ccm_paging_p=N&ccm_order_by=ak_date&ccm_order_by_direction=desc` (≈430 pages).
  - Per-court subpaths: `/court-appeal/`, `/court-first-instance/`, `/arbitration/`, `/small-claims-tribunal/` (unverified for SCT).
  - Judgment pages contain **full text in HTML** (verified: CA 003/2026 Al Buhaira v Arab War Risks).
  - The `?keywords=` form parameter exists, but the results looked like the default latest list, so the filter is unverified.
  - robots: `Disallow:` empty, i.e. allowed. **Tier C (good).**
- **ADGM Courts:** `https://www.adgm.com/adgm-courts/judgments` → 200, links to sealed PDFs on `assets.adgm.com/download/assets/…pdf/{hash}`. robots disallows `/api/`. Tier C (PDF extraction needed). ADGM legislation is on `adgm.com` / `en.adgm.thomsonreuters.com` (unverified).
- **Related project:** `neonsecret/ai-challenge-legal` (ARLC 2026 RAG over DIFC documents).

## 9. Saudi Arabia
- `laws.boe.gov.sa` (Bureau of Experts, the official consolidated statutes) and `boe.gov.sa`, `ncar.gov.sa` all **timed out from the UK**: geo-block or WAF. Tier D here, unverified elsewhere.
- `sjp.moj.gov.sa` (Scientific Judicial Portal) redirects to **`laws.moj.gov.sa`**, a Nuxt SPA "البوابة القانونية". Its bundle references the backend `https://laws-gateway.moj.gov.sa/apis/legislations/v1`, plus judicial-decision list components (`JudicialDecisionsList-courtTypes`). The gateway root returned 404, so the endpoint paths are unverified. Tier C/D.
- Arabic only (some English translations on BOE).

## 10. Qatar
- `almeezan.qa` (official Al Meezan legal portal): React SPA (200). The API base was not extracted. Content is legislation + some Court of Cassation rulings (unverified). Tier C (unverified).
- `qicdrc.gov.qa` (Qatar International Court, English common law): 200 HTML. The judgments listing was not inspected. Tier C (unverified).

## 11. Bahrain
- `legalaffairs.gov.bh` (Legislation & Legal Opinion Commission): 200, ASP.NET MVC HTML, routes `/Legislation/Search`, `/Treaty/Search`, `/LegalOpinion/Search`, `/Legislation/English`.
- Gotcha: `www.legalaffairs.gov.bh` has a TLS name mismatch, so use the bare host. The search query-param name is unverified. Tier C.
- Case law: no official open source found.

## 12. Oman
- `mjla.gov.om` (Ministry of Justice & Legal Affairs): 200 HTML.
- `qanoon.om`: **unofficial** (privately run) but comprehensive Arabic collection of Royal Decrees and laws. **WordPress REST works** (verified): `https://qanoon.om/wp-json/wp/v2/posts?search=<ar>&per_page=…`. robots only blocks wp-admin. Tier C+ (unofficial).

## 13. Kuwait
- `moj.gov.kw`: 200 (SharePoint, 1.3 MB homepage). `e-justice.gov.kw` does not resolve. No open case law or legislation API found. Tier D (unverified).

## 14. Jordan
- `lob.gov.jo` (Legislation & Opinion Bureau, official): 200, JS SPA, API not extracted. Tier C (unverified).
- Qistas (`qistas.com`) is the main case-law database and is **paid**. Tier D.

## 15. Lebanon
- `legiliban.ul.edu.lb` (Lebanese University Centre for Legal Informatics): ASP.NET HTML.
  - `Law.aspx?lawId=278573&language=ar` → 200, 102 KB (verified).
  - Search forms: `LegisltaionSearch.aspx` (sic) and `AdvancedRulingSearch.aspx`, so rulings exist too.
  - The ViewState-postback search is awkward to automate.
  - Tier C. Arabic (some French).
- Gotcha: the `www.` host does not resolve, so use the bare host.

## 16. Egypt
- `cc.gov.eg` (Supreme Constitutional Court): 200 HTML.
- No official free consolidated legislation. The commercial databases (Manshurat, Eastlaws) are paid. Tier D for legislation, C/unverified for SCC rulings.

## 17. Morocco
- `adala.justice.gov.ma` (MoJ legal portal): 200, Next/Nest app, PDFs under `/api/uploads/YYYY/MM/DD/…pdf`. Bulletin Officiel is on `sgg.gov.ma` (200, ASP.NET). Tier C (PDFs).
- Case law: `juriscassation.cspj.ma` and `cspj.ma` **timed out**. Tier D from the UK.
- Arabic/French.

## 18. Tunisia
- `legislation.tn` refused the connection (443) and returned 503 over http. `iort.gov.tn` (JORT) → 200, tiny shell. Tier D/C. No open case law found.

## 19. Algeria
- `joradp.dz` (Journal Officiel): 200, frameset HTML + PDFs (`/HAR/Index.htm`). Tier C (PDF only).
- `coursupreme.dz` timed out. Tier D.

---

## 20. International courts and bodies

### ICJ
- `https://www.icj-cij.org/list-of-all-cases` and `/case/{n}`, `/case/{n}/judgments`: 200 HTML (Drupal). Search: `/advanced-search?search_api_fulltext=genocide` → 200 with `/case/{n}` links (verified).
- **PDFs are Cloudflare-challenged** (verified 403 `cf-mitigated: challenge`). Example: `/sites/default/files/case-related/178/178-20220722-jud-01-00-en.pdf`. The pattern is `{case}-{yyyymmdd}-{JUD|ORD|ADV}-01-00-{en|fr}.pdf`.
- robots is permissive (standard Drupal). Tier C (metadata) / D (texts).

### ICC
- `icc-cpi.int/court-record/…` → **Gcore JS/cookie wall** (verified). Tier D directly.
- **Legal Tools Database** (CILRAP; holds ICC court records + ICTY/ICTR/national war-crimes material):
  - `https://legal-tools.org/api/ltddocs?filter={"limit":2,"where":{"title":{"like":"Ongwen","options":"i"},"organisation":"International Criminal Court (ICC)"},"fields":{…}}` → JSON with `externalId` (e.g. `ICC-01/12-01/15-86`), `dateCreated`, `slug`, `pdfURL` (`http://www.legal-tools.org/doc/{slug}/pdf/`).
  - `/api/ltddocs/count` → `{"count":441310}` (verified).
  - It is LoopBack: `where`/`like`/`fields`/`limit`/`skip`. Full-text search is not exposed via GET (`/api/search` 404).
  - **Undocumented. robots `use=reference`, ai-train=no, ClaudeBot disallowed.** Tier C+ technically, with a terms risk.

### ITLOS
- `https://www.itlos.org/en/main/cases/list-of-cases/` → 200 HTML (TYPO3). Case pages use slugs. PDFs download directly (verified: `/fileadmin/itlos/documents/cases/31/Advisory_Opinion/C31_Adv_Op_21.05.2024_orig.pdf` → 200 application/pdf).
- robots disallows `/en/main/ke-search/*` (its own search) and `/*?id=*`. Tier C. English/French.

### PCA
- `pca-cpa.org/en/cases/` and `pcacases.com/web/view/{id}` → **403 Cloudflare challenge**. `pcacases.com/web/allcases` loads a JS shell only. robots on pcacases: `ai-train=no, use=reference`, ClaudeBot disallowed. Tier D.

### WTO dispute settlement
- **No dispute API.** The WTO API portal (Azure APIM, free key) lists only **ePing, QR, Timeseries, TFAD** (verified via `apiportal.wto.org/developer/apis`).
- Case pages `wto.org/english/tratop_e/dispu_e/cases_e/ds600_e.htm` → 200 HTML (verified), with the status table at `dispu_status_e.htm`.
- Panel/AB reports live on `docs.wto.org`, whose **robots `Disallow: /` for all agents**.
- Tier C (wto.org case summaries) / D (docs.wto.org report texts).

### UN Treaty Collection
- `https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXI-6&chapter=21&clang=_en` → 200, 1.3 MB HTML (status, reservations, declarations). robots `Crawl-delay: 2`, otherwise allowed. There is no API. Tier C.

### ICSID / investment arbitration
- **`https://icsid.worldbank.org/api/all/cases`** → 200 JSON, 1.6 MB (verified). Shape: `{data:{GetAllCasesResult:[{caseid, caseno:"ARB/26/41", caseproceedings:[{claimant, respondent, arbitrators, dateregistered, …}], casedecisions:[{dcsntitle, dcsndate, docurl, docurlen/fr/sp, …}]}]}}`. It covers every case, with decision PDF links. It is undocumented but used by the site's case database. Tier C+ (good).
- Case detail HTML: `/cases/case-database/case-detail?CaseNo=ARB/20/1` → 200.
- **italaw.com** → 403 Cloudflare challenge. Tier D.
- Old scrapers exist: `s7minhas/icsidData` (2014) and `EngSciMath-team/ICSID-Cases` (2019), both stale.

### Inter-American Court of Human Rights
- `corteidh.or.cr` (including PDFs like `/docs/casos/articulos/seriec_520_esp.pdf` and `casos_sentencias.cfm`) → **403 Cloudflare challenge** (verified).
- `jurisprudencia.corteidh.or.cr` → 200, but it is a **vLex-hosted** SPA (recurly/vLex assets).
- Tier D. Spanish/English.

### African Court on Human and Peoples' Rights
- `african-court.org/cpmt/finalised` → 200 HTML (case-management listing). Tier C.
- **AfricanLII hosts AfCHPR judgments** under `/akn/aa-au/judgment/afchpr/…` (they appeared in ghalii and africanlii search results). Search works via the Peachjam API; the text is challenged.

### EFTA Court
- SPA backed by **`https://api.eftacourt.int/api`** (from `eftacourt.int/config.js`, verified):
  - `GET /api/cases` → JSON array of **463 cases**: `{id:"c-wp-10023", ref:"E-25/24", parties, status, type, procedure, source, referringCourt, language, subjectMatter[], keywords, description(HTML), diary[], dateSubmitted, hearingDate, judgmentDate, documents:[ids]}`.
  - `GET /api/cases/{id}` returns the same object for one case.
- There is no server-side search (`/api/search` 404). Filter client-side.
- The document text endpoint was not found: `/download/dc-…` redirects to a site search. Tier C+ (metadata) / text unverified. Undocumented.

### Eurasian Economic Union Court
- `courteurasian.org/court_cases/eaeu/` → 200 HTML (Bitrix). robots blocks Bitrix internals and `PAGEN` paging params. Tier C. Russian.

### CIS Economic Court (`sudsng.org`) and EACJ (`eacj.org`)
- Both timed out from the UK. Tier D (unverified). EACJ decisions may be on africanlii.

### ECOWAS Court
- `courtecowas.org` → 200 (WordPress). Decisions pages load. The WP REST API was not checked. Tier C.

---

## Gotchas / design implications for world-legal-mcp
1. **Bot walls are the main obstacle here, not missing APIs.** Cloudflare managed challenges (`cf-mitigated: challenge`) sit in front of SAFLII, most Peachjam document pages, ICJ PDFs, PCA, italaw, the IACtHR and uaelegislation. AWS WAF fronts Kenya Law and Gcore fronts the ICC. A plain-HTTP MCP cannot pass these, and passing them with a headless browser would contradict the stated content-signal reservations.
2. **Content-Signal `ai-input=no`** (Peachjam/Laws.Africa sites, legal-tools, pcacases) is a new, explicit EU-TDM-style opt-out from RAG/live-grounding use. Treat it as "not permitted" for an AI-facing MCP, even where curl works (e.g. NigeriaLII full text, Peachjam search JSON). The safe pattern is to return search metadata and snippets plus a link only. Even that arguably exceeds `search=yes`, which excludes AI-generated summaries.
3. **Geo-blocking/timeouts from a UK IP:** Saudi BOE, Morocco CSPJ, Algeria Supreme Court, Tunisia legislation.tn, Israel court decision sites, the CIS Economic Court and EACJ. A deployed server's location matters. Re-test from the deploy region before writing these off.
4. **Clean wins to build first:**
   - Knesset OData + Hebrew Wikisource (Israel legislation)
   - DIFC judgments HTML
   - ICSID `/api/all/cases`
   - EFTA `/api/cases`
   - ITLOS HTML + PDFs
   - WTO `ds{n}_e.htm`
   - UNTC ViewDetails
5. **Peachjam adapter:** one ~150-line adapter covers search for 17 sites, using a `{site_base}` config per country plus lowercase `doc_type` values and `page≤10`. Only build it if "search + outbound link" output is accepted, or obtains a Laws.Africa / Kenya Law API agreement.
