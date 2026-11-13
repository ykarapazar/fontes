# Asia-Pacific legal data sources — research for world-legal-mcp

Probed 2026-11-05 from a **UK IP**, curl with a Chrome UA, a handful of read-only GETs/POSTs per source.
"verified" means a request returned real data on 2026-11-05. "unverified" means not tested, or not
tested to the point of returning data. Tiers: **A** = official API, no key · **B** = official API, free key ·
**C** = HTML only, automated access allowed or not forbidden · **D** = paid, forbidden, blocked or nothing usable.

## Summary

| Jurisdiction | Case law tier | Legislation tier | Best endpoint | Auth | Notes |
|---|---|---|---|---|---|
| Australia (Cth) | C (FCA) / D (AustLII, HCA) | **A** | `api.prod.legislation.gov.au/v1` (OData v4) | none | FRL API verified, incl. EPUB/Word download. AustLII is behind a Cloudflare challenge (403) and its robots.txt doesn't grant `ai-input`. hcourt.gov.au timed out. |
| Australia (states) | C (NSW Caselaw, robots-disallowed) | B (Qld API) / C | `api.legislation.qld.gov.au` | free signup (Qld) | NSW legislation behind Cloudflare (403). Qld API is free with registration, CC BY 4.0. |
| New Zealand | C (courtsofnz RSS + PDF) | **B** | `api.legislation.govt.nz/v0/works` | key by email to PCO | Website is behind an AWS WAF challenge (202, empty body), so the API is the only route. NZLII is behind Cloudflare (403). |
| India | D (official sites use captchas; Indian Kanoon is paid) / bulk open data on S3 | **A** (de facto) | `indiacode.gov.in/server/api` (DSpace 9.1 REST) | none | India Code moved to DSpace 9, with keyword search and section-level items, verified. SC/HC judgments: AWS Open Data S3 buckets (CC-BY-4.0, updated Oct 2026). |
| Pakistan | D | D/C | pakistancode.gov.pk (HTML/PDF) | none | supremecourt.gov.pk returns Akamai "Access Denied" from the UK. Existing `pk-eli-mcp` uses static HF snapshots. |
| Bangladesh | C (unverified) | C | bdlaws.minlaw.gov.bd (HTML, UTF-16!) | none | Thin coverage. |
| Sri Lanka | D | C (CommonLII) | commonlii.org/lk | none | supremecourt.lk is behind Cloudflare (403). lawnet.gov.lk has a bad TLS cert. |
| Nepal | C (nkp.gov.np, unverified depth) | C | lawcommission.gov.np | none | Nepali language. Reachable. |
| Singapore | C | C | `sso.agc.gov.sg/Act/{code}` + `elitigation.sg/gd/s/{yyyy_COURT_n}` | none | SSO robots.txt: `Disallow: /search`, `Crawl-delay: 6`, AWS WAF. eLitigation keyword search works over GET. |
| Malaysia | D/C | C | lom.agc.gov.my (PDF) | none | Existing `my-eli-mcp`. Court judgments: kehakiman portal (unverified). |
| Hong Kong | C (HKLII, robots-disallowed API; legalref) | C (live) / A (bulk ZIP) | `hklii.hk/api/advancedsearch` (undocumented JSON) | none | eLegislation site has a JS client check. DoJ open data is bulk XML ZIPs on data.gov.hk. |
| China | D | **A** (undocumented) | `flk.npc.gov.cn/law-search/search/list` (POST JSON) | none | New flk SPA (2025) JSON API verified; DOCX via signed OBS URL. China Judgments Online requires login and phone number, so it is not usable. |
| Taiwan | C (FJUD HTML) / B-ish (JY open data, unreachable) | **A** (bulk) / C (per article) | `law.moj.gov.tw/api/Ch/Law/JSON` (zip) + `LawSingle.aspx` | none | data.judicial.gov.tw timed out from the UK. `legaltechtw/taiwan-law-mcp` already exists (remote, no key). |
| Japan | D right now (courts.go.jp hanrei search "under maintenance") | **A** | `laws.e-gov.go.jp/api/2` | none | Best legislation API in the region: keyword search, article-level access, JSON. Several MCPs already exist. |
| South Korea | **B** | **B** | `www.law.go.kr/DRF/lawSearch.do?OC=…` | free OC id + **registered server IP/domain** | Covers both case law and legislation. `chrisryugj/korean-law-mcp` (★2.8k, MIT) is dominant. |
| Philippines | C | C | lawphil.net (static HTML), elibrary.judiciary.gov.ph | none | No API. Predictable static URLs. |
| Indonesia | D (MA putusan behind Cloudflare 403) | C | peraturan.bpk.go.id/Search | none | peraturan.go.id and jdihn.go.id timed out from the UK. |
| Thailand | D (deka timed out) | D/C (krisdika self-signed cert; ocs.go.th SPA) | — | — | Thai only. Not worth it in v1. |
| Vietnam | D (congbobanan TLS reset) | C (vbpl.vn) | vbpl.vn | none | anle.toaan.gov.vn (precedents, Oracle ADF) is reachable. Vietnamese only. |
| Pacific (PacLII) | D | D | paclii.org | — | Same AustLII/Cloudflare stack: case pages and search return 403. |

---

## Australia

### Legislation — Federal Register of Legislation (FRL), **Tier A, verified working 2026-11-05**
- Base: `https://api.prod.legislation.gov.au/v1/` — **OData v4**, JSON, no key. `$metadata` (30 KB EDMX) lists the entity sets
  `Titles, Versions, Documents, Content, Affect, TextApplies, …` and the bound functions `Search` (on Titles, Versions, TextApplies)
  and `Find` (on Versions and Documents).
- Identifier: **title ID**, e.g. `C2004A00818` (Corporations Act 2001). `C{year}A{nnnnn}` = as-made Act. `C{year}C{nnnnn}` = compilation (registerId).
  `F{year}L…` = legislative instruments.
- Examples (all returned 200 on 2026-11-05):
  - `GET /v1/titles?$top=2` — paged title list (`@odata.count` available).
  - `GET /v1/titles('C2004A00818')` — title metadata: status, isInForce, collection (Act / LegislativeInstrument / …).
  - `GET /v1/titles/Search(criteria='and(text("privacy",name,contains),pointintime(Latest))')?$top=2` — **title search**. 158 hits.
  - `GET /v1/versions/find(titleId='C2004A00818',asAtSpecification='Latest')` — current compilation (Corporations Act: compilation 149,
    registerId `C2026C00432`, in force since 2026-09-19), plus `reasons[]` with amending-Act links. `asAtSpecification` ∈ `Latest|AsMade|Current`. `asAt=` is available for point-in-time lookups.
  - `GET /v1/documents?$filter=registerId eq 'C2026C00432'` — lists Word/PDF files per **volume** (big Acts are split into 7 volumes).
  - **Full text:** `GET /v1/documents/find(titleid='C2004A00818',asatspecification='Latest',type='Primary',format='Epub',uniqueTypeNumber=0,volumeNumber=0,rectificationVersionNumber=0)`
    returned a **2.3 MB EPUB** (zip of XHTML), a single file for the whole Act. Use EPUB rather than PDF. `format='Word'` needs `volumeNumber` 1..n. The Word variant with volumeNumber=0 returned 404.
- Full-text (body) search: the `text(...,content,contains)` / `text,contains` criteria returned `400 cannot parse text`. **Body search is unverified.**
  Only title search is confirmed. Per-section access isn't available from the API: split the EPUB XHTML on headings. The website HTML `/C2004A00818/latest/text`
  is 2.8 MB Angular SSR with few anchors, so it's no help.
- Licence: CC BY 4.0 (FRL "data share and reuse" page). The API is undocumented-public: it's the backend of the Angular site. There's no published rate limit.
- Existing: `matematicsolutions/au-eli-mcp` (Apache-2.0, pushed 2026-09-24): FRL **Acts only**, title search plus truncated text.
  `specializedtom/legislation` (tiny). `konashevich/olexi-mcp` (AustLII search; it will hit the Cloudflare wall described below).

### States — legislation
- **Queensland:** official **API Service**, free with registration at `https://api.legislation.qld.gov.au/api/signup`. Base `https://api.legislation.qld.gov.au/` (Swagger).
  Content is **CC BY 4.0**. Terms allow rate limits and revocation. **Tier B.** Signup page verified, API calls unverified (no key).
  Website `legislation.qld.gov.au/view/html/inforce/current/act-1899-009` returned 200 HTML.
- **NSW:** `legislation.nsw.gov.au` returned a **Cloudflare challenge (403)** to curl. Runs the same PCO platform family as Qld. An API is unverified.
- **Victoria:** `legislation.vic.gov.au` returned 200 (Nuxt SSR). No API checked.

### Case law
- **AustLII** (`austlii.edu.au`, `www8.austlii.edu.au`): **every case page and `sinosrch.cgi` search returned 403 "Just a moment…" (Cloudflare managed challenge)**
  even with a Chrome UA. robots.txt: `Content-Signal: search=yes, ai-train=no, use=reference` and **no `ai-input` grant**. It blocks ClaudeBot/GPTBot/CCBot by name,
  and it frames the signals as an EU DSM Art. 4 rights reservation. **Tier D** for a live-fetching AI tool. The same infrastructure blocks NZLII, PacLII and CommonLII case pages.
  (CommonLII index pages `commonlii.org/my/`, `/lk/` returned 200.)
- **High Court of Australia:** `hcourt.gov.au` → HTTP/2 INTERNAL_ERROR, then a timeout (3 attempts, both IPv4 and HTTP/1.1). It may be geo- or bot-filtered. **Unverified.**
- **Federal Court:** judgment HTML returned 200, e.g. `https://www.judgments.fedcourt.gov.au/judgments/Judgments/fca/single/2024/2024fca0001`.
  The RSS `https://www.judgments.fedcourt.gov.au/rss/fca-judgments` returned 200 (1.9 MB). The search UI `fedcourt.gov.au/digital-law-library/judgments/search` is JS-driven.
  The old Funnelback host `search2.fedcourt.gov.au` no longer resolves, and `search.fedcourt.gov.au` timed out. Keyword search is **unverified**. **Tier C**: fetch by citation plus the latest-judgments RSS.
- **NSW Caselaw** (`caselaw.nsw.gov.au/search/advanced?body=…`): returned 200 HTML with keyword search, **but robots.txt reads `# go away` / `Disallow: /decision /search`**,
  and pages carry `noindex,nofollow`. Technically C, policy D.
- **Queensland** `sclqld.org.au/collections/caselaw`: returned 200 (Nuxt SSR, 925 KB). API unverified.
- Bulk alternative: the Isaacus/Umar Butler "Open Australian Legal Corpus" (HF) is a snapshot, not live, so it's out of scope. Unverified this session.

## New Zealand

### Legislation — **Tier B**
- API: `https://api.legislation.govt.nz/v0/` with endpoints works search, versions of a work, and a specific version (per the developer page).
  `GET /v0/works?search_term=privacy` returned **401 `{"error":"API key is required"}`** (verified 2026-11-05).
- **Key: request by email to contact@pco.govt.nz.** The key is tied to name and email, under "API terms of use" (`legislation.govt.nz/learn-more/legislation-data/api-terms-of-use/`).
  Free, but manual issuance. Each user of an open-source MCP would need their own key, or we document a BYO-key env var.
- The website `www.legislation.govt.nz` (including `/act/public/2020/0031/latest/whole.html` and the `.xml` variants) returned **202 with an empty body and `x-amzn-waf-action: challenge`** (CloudFront LHR).
  HTML/XML scraping is therefore **blocked without a JS solve**, and the API is the only viable route. Identifier: `act/public/2020/0031` (year/number), with `LMS…` provision ids.
- Existing MCP: none found on GitHub ("new zealand legislation mcp": 0 hits).

### Case law — **Tier C**
- `courtsofnz.govt.nz/judgments/supreme-court` returned 200 HTML. **RSS** `…/judgments/supreme-court/RSS` returned 200 (public-interest judgments only).
  PDFs at `/assets/cases/2026/2026-NZSC-122.pdf`. No keyword search API.
- Ministry of Justice Judicial Decisions Online (`forms.justice.govt.nz/search/…`) reset the connection from the UK. **Unverified.**
- NZLII: Cloudflare 403, same as AustLII. **D.** `udmada/nzlii` (a Cloudflare workflow repo) exists but wasn't evaluated.

## India

### Legislation — India Code, **Tier A (de facto), verified working 2026-11-05**
- **Big change:** `indiacode.nic.in` now meta-refreshes to **`indiacode.gov.in`**, an Angular frontend on **DSpace 9.1**.
  The old `/handle/…/simple-search` timed out. The **DSpace REST API is open and anonymous**:
  - `GET https://indiacode.gov.in/server/api` — root (`dspaceVersion: "DSpace 9.1"`).
  - `GET /server/api/discover/search/objects?query=contract%20act&size=2&dsoType=ITEM` — Solr search with hitHighlights. Supports `query=dc.title:"Indian Contract Act"`.
  - Items carry rich metadata: `dc.identifier.act_id` (e.g. `AC_CEN_3_20_00035_187209_1523268996428`), `act_number`, `state_name` (CENTRAL or a state), `ministry_name`, `enforcement_date`, `repealed`.
  - **Section-level items exist** (`dc.identifier.collection = SECTION`): e.g. the search `"free consent"` returns s.14 of the Indian Contract Act, with the section text as HTML in
    `dc.identifier.section_page_note`, plus `section_number` and `act_id` linking it to the parent Act.
  - Full Act: `GET /server/api/core/items/{uuid}/bundles` → ORIGINAL bundle (PDFs, English + Hindi) and **TEXT bundle (`a1872-9.pdf.txt`, 181 KB extracted text)**.
    `GET /server/api/core/bitstreams/{uuid}/content` returned the text (verified).
- Gotchas: duplicate items for state adaptations, e.g. Contract Act ×2 (Chhattisgarh plus Central), so filter `state_name=CENTRAL`. Item URIs still say `test1.indiacode.nic.in`,
  a fresh migration, so expect churn. The API is generic DSpace, not a documented India Code product. robots.txt returned 500. There's no stated rate limit.
  "Consolidated" means India Code's updated text, but amendment currency is uneven (known issue, unverified here).

### Case law
- **Supreme Court** `sci.gov.in/judgements-judgement-date/` returned 200, but search needs a **CAPTCHA** (verified in the HTML). `main.sci.gov.in` doesn't resolve.
- **eCourts judgments portal** `judgments.ecourts.gov.in/pdfsearch/` returned 200 with an **image/audio CAPTCHA**. **D** for live use.
- **Indian Kanoon:** the website is behind a Cloudflare challenge (403). The API `api.indiankanoon.org/search/?formInput=…` returned 401 without credentials.
  **Paid prepaid API**: search Rs 0.50/call, document Rs 0.20, fragment Rs 0.05, metainfo Rs 0.02. Rs 500 free trial credit. Non-commercial users can apply for up to Rs 10k/month
  (manually verified). Attribution required. Auth by token or public/private key. **Tier D (paid)**, though cheap enough to offer as BYO-token.
- **Bulk open data (best free option):** AWS Open Data buckets `s3://indian-supreme-court-judgments` (us-east-1) and `s3://indian-high-court-judgments` (ap-south-1).
  Anonymous ListBucket is verified. Layout `metadata/{json,parquet,tar}/year=YYYY/…`, `data/{pdf,tar}/…`, HC adds `metadata/parquet_case_details/`.
  SC 2026 metadata `LastModified 2026-10-17`. CC-BY-4.0 (per the dataset listing, unverified this session). No full-text search: you'd have to query the parquet metadata (e.g. with DuckDB over HTTP),
  which is borderline "bulk indexing". Fine for fetch-by-case though.
- Existing MCPs: `CHANDAN2901/indian-legal-mcp` (MIT, ★0, Indian Kanoon + Supabase), `GSMS-B/indian-legal-mcp` (★1), `deveshmaster/Indian-Kanoon-MCP-Server` (stale 2025-07).
  **None for India Code's new API.**

## Pakistan / Bangladesh / Sri Lanka / Nepal (light)
- **Pakistan:** `pakistancode.gov.pk/english/` returned 200 (HTML index plus PDFs, no API). `supremecourt.gov.pk/judgement-search/` returned **Akamai "Access Denied" (403) from the UK**.
  `matematicsolutions/pk-eli-mcp` (Apache-2.0) is **corpus-based**: HF snapshots of 967 statutes (to 2025-01-30) and 1,414 SC judgments (to 2024-07-26), so it isn't live. Legislation C, case law D.
- **Bangladesh:** `bdlaws.minlaw.gov.bd` returned 200, **served as UTF-16** (decode carefully). It has section-wise HTML (`act-details-NNN.html`, unverified).
  `supremecourt.gov.bd/web/` returned 200 (judgment PDFs, unverified). Tier C/C.
- **Sri Lanka:** `supremecourt.lk` returned Cloudflare 403. `lawnet.gov.lk` has a TLS hostname mismatch. CommonLII `/lk/` index returned 200, but case pages sit on the AustLII stack (likely 403). Tier D/C.
- **Nepal:** `nkp.gov.np` (Nepal Kanoon Patrika, SC reported judgments) returned 200. `lawcommission.gov.np` (Acts) returned 200 (239 KB). Nepali, HTML/PDF. Tier C/C (unverified depth).

## Singapore

### Legislation — Singapore Statutes Online (SSO), **Tier C**
- `https://sso.agc.gov.sg/Act/{ActCode}`, e.g. `/Act/PDPA2012`, `/Act/CA1967`. Returned 200 HTML. Provision anchors are `id="pr{n}-"`.
- Gotcha: **only the first ~5 provisions are in the initial HTML.** The rest lazy-loads via `/Details/GetLazyLoadContent?…` (data-term GUIDs).
  `?ProvIds=pr26-` and `?WholeDoc=1` did **not** change that. You need to replay the lazy-load calls, or use the PDF/print view (unverified).
- **robots.txt: `Disallow: /search`, `Crawl-delay: 6`.** Search timed out for us anyway. Behind **AWS WAF**: `/Terms-of-Use` and `/Help/Copyright` returned 202 (challenge) and WebFetch got 403.
  So **the terms text is unverified**. Point-in-time versions exist (`?ValidDate=`, unverified).
- Existing: `matematicsolutions/sg-eli-mcp` (Apache-2.0, 2026-10-08). It browses the Acts list, fetches a section or full text, and deliberately does no search to respect robots.
  Also `kevanwee/sgstatutescraper` (MIT).

### Case law — eLitigation, **Tier C**
- Search: `GET https://www.elitigation.sg/gd/Home/Index?Filter=SUPCT&YearOfDecision=All&SortBy=DateOfDecision&CurrentPage=1&SearchPhrase=negligence` returned 200 with result
  links `/gd/s/2026_SGCA_43`, `/gd/s/2026_SGDC_317`. **Full-text keyword search over plain GET works.**
- Document: `https://www.elitigation.sg/gd/s/2024_SGCA_1` returned 200 with full judgment HTML. Identifier = neutral citation `[2024] SGCA 1` → `2024_SGCA_1`.
- Coverage: SGCA/SGHC/SGHCR/SGDC/SGMC/SGFC etc. Free coverage is roughly 2000+ for the superior courts (unverified). LawNet holds older and paid material (**D**).
- robots.txt returned 404 (none). Terms page not found. © Government of Singapore. Terms are **unverified**.
- Existing: scrapers only (`kevanwee/elitiscraper` MIT, `juliusalberto/scraper-elitigation`). **No eLitigation MCP found.**

## Malaysia (light)
- Legislation: `lom.agc.gov.my` returned 200. Principal Acts are published as **PDF only**, with no search API (per `matematicsolutions/my-eli-mcp`, Apache-2.0). Tier C.
- Case law: `kehakiman.gov.my` returned 200 (judgments portal, unverified). CommonLII `/my/` index returned 200. CLJ and MLJ are paid. Tier D/C.

## Hong Kong

### Legislation
- eLegislation `https://www.elegislation.gov.hk/hk/cap32!en` redirects to `/checkconfig/checkClientConfig.jsp` (**JS/cookie client check**). Plain curl can't reach content. `cap1!en.xml` returned 404.
- **Open data (Tier A, but bulk only):** data.gov.hk CKAN `GET https://data.gov.hk/en-data/api/3/action/package_search?q=legislation` (verified). Datasets
  `hk-doj-hkel-legislation-current` and `-past` are **ZIPs of XML** split by Cap range, e.g. `https://resource.data.one.gov.hk/doj/data/hkel_c_leg_cap_1_cap_300_en.zip`, plus `…_instruments_en.zip`, in EN and TC.
  This conflicts with the "no bulk" rule unless we download one ZIP per call and cache in memory.
- Identifier: `Cap {n}` / `cap{n}!en/s{section}`.

### Case law
- **HKLII** (`hklii.hk`, rebuilt as a Vue SPA): an undocumented JSON API works:
  `GET https://www.hklii.hk/api/advancedsearch?searchType=advanced&text=negligence&dbs=…&page=1` returned 200 JSON with 1,161 hits, mixing ordinances
  (`path:"/en/legis/ord/71/s7"`) and cases. `getcasedetail` returned 404 or timed out with our guessed params, so the document endpoint is unverified.
  **robots.txt: `Disallow: /api`**, so policy is D unless HKLII gives permission (it's run by HKU, so asking is realistic).
- **Judiciary Legal Reference System** `legalref.judiciary.hk/lrs/common/ju/judgment.jsp` returned 200. Frameset JSP, judgments by `DIS=` id. Fetchable, but search is form/frame based. Tier C.
- Existing: no HK MCP found (`JackieFong999/LawyerAICaseVerify` is just a citation checker).

## China

### Legislation — National Database of Laws and Regulations (国家法律法规数据库), **Tier A (undocumented), verified working 2026-11-05 from the UK**
- The site was rebuilt as a Vue SPA. API paths come from `/assets/index-*.js`:
  - Search: `POST https://flk.npc.gov.cn/law-search/search/list`, JSON body
    `{"searchRange":1,"sxrq":[],"gbrq":[],"searchType":2,"sxx":[],"gbrqYear":[],"flfgCodeId":[],"zdjgCodeId":[],"searchContent":"民法典","pageNum":1,"pageSize":2}`
    returned `{"total":909,"rows":[{bbbs,title,gbrq(published),sxrq(effective),sxx(status),zdjgName(issuer),flxz(type)…}]}`. An incomplete body returns `{"code":500}`.
    `searchRange`/`searchType` probably switch between title and full text (unverified which value).
  - Detail: `GET /law-search/search/flfgDetails?bbbs={id}` returns metadata, `lsyg` (version history), and `content` (**TOC tree only**, not the article text).
  - Text: `GET /law-search/download/pc?bbbs={id}&format=docx` returns a **signed URL** on `flkoss.obs-bj2.cucloud.cn` → DOCX (verified: 21 KB valid Word file). OFD and PDF also exist.
  - `/law-search/index/captchaImage` exists, so captcha may be imposed on some flows or under load.
- Identifier: `bbbs` (32-hex version id). It's per **version**, not per law. Article-level access means parsing the DOCX.
- No published ToS on API use. The site is a mainland government portal, so expect throttling.
- Existing: `lawtext/laws` (★126, a mirrored corpus, not an MCP). A Kotlin app uses the flk API. **No MCP.**

### Case law — **Tier D**
- China Judgments Online `wenshu.court.gov.cn` returned 200 on the homepage, but search and documents need **login with a mainland mobile number**, plus heavy JS anti-bot.
  Publication volume has been sharply reduced since ~2021-22 (widely reported, unverified here). The 人民法院案例库 (`rmfyalk.court.gov.cn`) homepage returned 200. It requires registration (unverified).
  Treat as unusable.

## Taiwan

### Legislation — MOJ Laws & Regulations Database, **Tier A (bulk) / C (per article)**
- Open data: `GET https://law.moj.gov.tw/api/Ch/Law/JSON` returned **a 6.1 MB ZIP of all laws** (verified). Variants exist for `/api/Ch/Order/JSON`, `/api/En/…`, and XML (pattern unverified).
- Per article (HTML): `https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=184` (Civil Code art. 184) returned 200. The whole law is at `LawAll.aspx?pcode=B0000001`.
  Identifier = `pcode`. Open Government Data Licence (TW), unverified this session.
### Case law
- FJUD `judgment.judicial.gov.tw/FJUD/default.aspx` returned 200. GET `qryresult.aspx?kw=…` returned 200 but no result links: it needs the ASP.NET POST/viewstate flow. Tier C.
- Judicial Yuan open data (`data.judicial.gov.tw` / `opendata.judicial.gov.tw`) had a **TCP connect timeout from the UK**, which looks like a geo or IP block.
  Its judgment API historically has a free account and limited service hours (unverified). Tier B/D depending on location.
- Existing: **`legaltechtw/taiwan-law-mcp`** (MIT; a public remote server at `https://legaltech.org.tw/mcp`, no key; covers statutes, judgments, constitutional court and legislative history.
  The GitHub repo holds only packaging, no source). Hosting from a TW-reachable region seems to be needed for JY data.

## Japan

### Legislation — e-Gov 法令API v2, **Tier A, verified working 2026-11-05**
- Base `https://laws.e-gov.go.jp/api/2/` (Digital Agency), JSON or XML, no key:
  - `GET /laws?law_title=民法&limit=2` returned `total_count` 11 with `law_info` + `revision_info` (`law_id` `129AC0000000089`, `law_revision_id` `129AC0000000089_20260624_508AC0000000045`).
  - `GET /keyword?keyword=個人情報&limit=2` — **full-text keyword search over the bodies of laws in force** (2,802 hits, with sentence snippets).
  - `GET /law_data/129AC0000000089?elm=MainProvision-Part_1-Chapter_1-Article_1&response_format=json` returns a **single article**. Omit `elm` for the whole law.
    `asof=` gives point-in-time versions. Also `/revisions/{law_id}` and `/attachment` (from the docs, unverified).
- Identifier: `law_id`, e.g. `{era-year}{type}{number}`: `129AC0000000089` = Meiji 29 Act No. 89. The JSON body is a nested tag tree (`{tag, attr, children}`), so you need a flattener.
- Licence: open data (government standard terms, CC BY 4.0-compatible). Japanese only, though the Japanese Law Translation site has English for some laws (no API, unverified).
- Existing MCPs (many): `matematicsolutions/jp-eli-mcp` (Apache-2.0), `kuro6061/e-gov-mcp` (MIT), `COREkin/japan-law-mcp` (MIT), `pipeworx-io/mcp-japan-law` (MIT, 2026-11-02), `geonwoo-jeong/japanese-law-mcp`.
### Case law — courts.go.jp 裁判例検索
- `courts.go.jp/hanrei/search1/index.html` and `/app/hanrei_jp/*` **redirect to `/error_document/sorry.html` ("メンテナンス中 / Maintenance")** on 2026-11-05 (2 checks, ~10 min apart).
  The homepage is up. The site was reorganised (`/hanrei/search{1..7}/index.html?courtCaseType=…`). It has historically been HTML only, with PDFs for full text and a selective
  subset of decisions. **Unverified / Tier C at best.** Commercial databases (D1-Law, Westlaw Japan, LEX/DB) are paid.

## South Korea — 국가법령정보 공동활용 Open API, **Tier B (both case law and legislation)**
- `GET https://www.law.go.kr/DRF/lawSearch.do?OC={id}&target={law|prec|detc|expc|admrul|ordin…}&type={JSON|XML|HTML}&query=…` and `lawService.do?…&ID=` / `MST=` for documents.
  - Verified response without a registered key: 200 with `{"result":"사용자 정보 검증에 실패하였습니다.","msg":"…정확한 서버장비의 IP주소 및 도메인주소를 등록해 주세요."}`.
    That means the **OC (your registered e-mail id) plus a whitelisted server IP/domain** are required. Free registration at `open.law.go.kr`.
  - Targets cover **legislation (current consolidated text, article-level `JO=`), Supreme Court and lower-court precedents (`prec`), Constitutional Court (`detc`), interpretations (`expc`), admin rules, local ordinances.**
    Full-text keyword search is available for both laws and precedents.
- Gotcha for an open-source local MCP: the IP whitelist means each end user must register their own IP. Dynamic home IPs break it, and that's why `korean-law-mcp` runs a hosted proxy.
- Existing: **`chrisryugj/korean-law-mcp`** (★2,842, MIT, active 2026-11-05; 42 API endpoints wrapped as 10 tools; hosted at `https://mcp.gomdori.app/law?oc=…`, which also works without a key on a shared quota).
  Also `SeoNaRu/korean-law-mcp`, `seo-jinseok/korean-law-mcp`. **Don't duplicate. Wrap it or link to it.**
- Supreme Court portal `portal.scourt.go.kr` returned 200 (SPA). Not needed given law.go.kr `prec`.

## Philippines (light) — Tier C / C
- **Lawphil** (Arellano Law Foundation): static HTML, predictable URLs. Monthly index `https://lawphil.net/judjuris/juri2023/jan2023/jan2023.html` returned 200 with links `gr_{number}_{year}.html`.
  Statute example `https://lawphil.net/statutes/repacts/ra2012/ra_10173_2012.html` (Data Privacy Act) returned 200, encoded windows-1252. No robots.txt (404). No search API.
- **SC E-Library** `elibrary.judiciary.gov.ph/thebookshelf/showdocs/1/69190` returned 200 with full decision HTML (G.R. No. 253355). It has a search form (unverified programmatically).
  `sc.judiciary.gov.ph/decisions/` returned 200 (WordPress).
- No MCP found.

## Indonesia (light)
- Legislation: `peraturan.bpk.go.id/Search?keywords=perlindungan+data+pribadi` returned 200 HTML results (BPK JDIH, the best coverage, PDFs). `peraturan.go.id` and `jdihn.go.id` timed out from the UK. Tier C.
- Case law: `putusan3.mahkamahagung.go.id` returned **Cloudflare 403**. Tier D from outside ID (unverified whether ID IPs pass).

## Thailand / Vietnam (light)
- **Thailand:** `krisdika.go.th` has a self-signed TLS cert. `ocs.go.th/council-of-state` is a hash-routed SPA (404 on the deep link). `deka.supremecourt.or.th` timed out. Thai only. **D** for v1.
- **Vietnam:** `vbpl.vn` (MOJ legal documents database) returned 200 with an anti-bot script (`/_fec_sbu/`). `phapdien.moj.gov.vn` (code of law) timed out. `congbobanan.toaan.gov.vn` (published judgments) TLS reset.
  `anle.toaan.gov.vn` (official precedents, Oracle WebCenter) returned 200. **Legislation C, case law D.**

## Pacific — PacLII
- `paclii.org` homepage returned 200, but **case pages (`/fj/cases/FJSC/2023/1.html`) and `sinosrch.cgi` return Cloudflare 403**, the same as AustLII.
  PacLII is the only aggregator for Fiji/PNG/Samoa/Vanuatu/Tonga etc., so the whole Pacific is **D** unless AustLII/PacLII grant access (it's worth emailing them: AustLII is a non-profit with a long open-access mission).

## Cross-cutting gotchas
1. **The *LII family (AustLII, NZLII, PacLII, CommonLII content, Indian Kanoon) now all sit behind Cloudflare challenges.** Without a headless browser plus permission, they're out.
   AustLII's robots.txt explicitly withholds `ai-input`.
2. **WAF challenges (AWS WAF: NZ legislation site, SSO; Akamai: SC Pakistan)** give 202/403 with an empty body. Detect `x-amzn-waf-action` and fail loudly instead of returning empty results.
3. **Geo-blocks/timeouts seen from the UK:** Taiwan Judicial Yuan open data, Indonesia peraturan.go.id/jdihn, Thailand deka, Vietnam congbobanan/phapdien, Sri Lanka lawnet, HCA (possibly).
4. **Undocumented-but-official JSON backends** (FRL OData, India Code DSpace, flk.npc, HKLII) are the real wins, and also the most fragile. Add contract tests that hit one known id daily.
5. **BYO-key jurisdictions:** NZ (email PCO), Korea (OC + IP whitelist), Qld (signup), Indian Kanoon (paid). Model these as optional env vars and leave tools disabled when they're unset.
