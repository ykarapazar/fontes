**Fontes — Round 2 source research**  
**Checked: 7 November 2026. Repository unchanged.**

Read the requested signup notes, adapter comments, Round 1 reports and validation reports before testing.

**Verification labels:** **VERIFIED** means the specified page, search or document worked during this round—not that the entire collection or its reuse permission was verified. **UNVERIFIED** identifies unresolved claims or access. Direct tests used an identifiable Fontes User-Agent. No registrations, bulk downloads or bot-check bypasses were performed.

Counts below are publisher estimates unless stated otherwise. A missing robots file is not permission. Where terms could not be obtained, copyright, automation and AI/TDM permissions remain unresolved. No geographic restriction was established by these tests.

---

**`it` — CASE LAW**

**1. Corte costituzionale and its open-data portal — official; conditional candidate.**

- **URLs/coverage:** [Court](https://www.cortecostituzionale.it/) and [open data](https://dati.cortecostituzionale.it/). Constitutional Court decisions, Italian, 1956 onward; portal descriptions give approximately 18,000–20,000 decisions, with inconsistent totals.
- **Machine access:** `/scheda-pronuncia/{year}/{number}` serves full HTML. [Decision 183/2026](https://www.cortecostituzionale.it/scheda-pronuncia/2026/183) returned substantive judgment text directly. The [download catalogue](https://dati.cortecostituzionale.it/Scarica_i_dati/Scarica_i_dati) offers XML/CSV/JSON archives; these are bulk packages, not a verified per-document API. Its linked `/sparql/snorql` interface returned 404.
- **Terms:** The [data portal](https://dati.cortecostituzionale.it/) states: “I dati disponibili in vari formati sono rilasciati con licenza Creative Commons (CC BY SA 3.0) per il libero riuso.” This explicitly covers its datasets; do not automatically extend that licence to every part of the main website.
- **Robots/blocks:** Main-site [robots.txt](https://www.cortecostituzionale.it/robots.txt) returned 404; [data-host robots.txt](https://dati.cortecostituzionale.it/robots.txt) returned 200 with an empty body. `/elenco-pronunce` redirected to a **Radware CAPTCHA**; `/ricerca-pronunce` did not yield a usable search.
- **Status:** **VERIFIED:** individual judgment HTML, dataset catalogue and licence. **UNVERIFIED:** usable live search/API. Promising for citation retrieval, not currently a verified complete search adapter.

**2. Giustizia amministrativa — official; restricted candidate.**

- **URL/coverage:** [Portal](https://www.giustizia-amministrativa.it/), Consiglio di Stato and regional administrative courts; Italian. Current total and earliest coverage not established this round.
- **Machine access:** Existing research identifies `visualizza` routes using `schema`, `nrg` and `nomeFile`, plus PDF documents. No individual judgment or working search was newly verified.
- **Terms:** [Conditions](https://www.giustizia-amministrativa.it/web/guest/condizioni-di-utilizzo) permit specified study/professional/cultural uses, “ma comunque non commerciali”; §1.5 prohibits mass automated access. The CC BY-NC-ND provision concerns scholarly articles—it is **not a blanket judgment licence**.
- **Robots/blocks/status:** [robots.txt](https://www.giustizia-amministrativa.it/robots.txt) returned 404. **VERIFIED:** terms. **UNVERIFIED:** retrieval and whether Fontes’s intended distribution fits the restrictions.

Also checked [Cassation legal notices](https://www.cortedicassazione.it/it/note_legali.page): “solo per uso personale”, with additional noncommercial restrictions for SentenzeWeb. Its robots request timed out. Not shortlisted.

---

**`jp` — CASE LAW**

**1. Courts of Japan, including the IP High Court static collection — official; usable narrow subset.**

- **URLs/coverage:** [National judgments portal](https://www.courts.go.jp/hanrei/) and [IP High Court Grand Panel index](https://www.courts.go.jp/ip/hanrei/g_panel/index.html). Japanese judgments. The static index has **16 numbered groups of concluded cases, 2005–2025**; some groups contain multiple decisions. Nationwide collection size was not established.
- **Machine access:** The static index links directly to text PDFs. [March 2025 Grand Panel judgment](https://www.courts.go.jp/ip/vc-files/ip/2025/hanketsuzenbun-r5ne10040.pdf) opened as a readable 50-page PDF. Another working document route is [`/assets/hanrei/hanrei-pdf-89254.pdf`](https://www.courts.go.jp/assets/hanrei/hanrei-pdf-89254.pdf). Follow actual links; filenames are not uniformly predictable.
- **Search:** [`/hanrei/search1/index.html`](https://www.courts.go.jp/hanrei/search1/index.html) redirected to a maintenance page. No working national keyword API verified. The small static index can support bounded listing/filtering.
- **Terms:** [Site policy](https://www.courts.go.jp/outline/index.html): “著作権法上認められている利用を行うことができます。” It permits uses recognized by copyright law and also says “裁判所に無断で改変を行うことはできません。” No explicit automation or AI/TDM prohibition found on that page; no CC licence claimed.
- **Robots:** [robots.txt](https://www.courts.go.jp/robots.txt) contains specific service-notice exclusions, e.g. `Disallow: /ip/tetuduki/kozisotatu/index.html`; no exclusion for the tested judgment paths.
- **Status:** **VERIFIED:** static index, judgment PDFs, policy and robots. **UNVERIFIED:** national search restoration. No login encountered.

---

**`au` — CASE LAW, federal courts and High Court**

**None found meeting all requirements.**

**1. AustLII — LII; permission/access unresolved.**

- **URL/coverage:** [AustLII](https://www.austlii.edu.au/), including HCA/FCA/FCAFC collections, English. Exact current years and counts were not verified.
- **Machine access:** Established HTML structure such as `/au/cases/cth/HCA/{year}/{number}.html`; no working judgment/search newly verified.
- **Terms:** [Copyright page](https://www.austlii.edu.au/austlii/copyright.html) returned 403. Search-indexed text from its [2023 annual report](https://classic.austlii.edu.au/austlii/reports/2023/AustLII_YiR_2023.pdf) describes blocking automated case-law access, but the PDF itself also returned 403. Treat that as historical, index-only evidence.
- **Robots:** Current [robots.txt](https://www.austlii.edu.au/robots.txt) includes `Content-Signal: search=yes,ai-train=no,use=reference` and a general `Allow: /`, alongside named-bot restrictions. This does **not resolve the terms discrepancy**.
- **Status:** **VERIFIED:** current robots. **UNVERIFIED:** current reuse permission and usable document access.

**2. JADE / BarNet — other, nonprofit legal-information service; unresolved.**

- **URL/coverage:** [JADE](https://jade.io/), Australian judgments, English; current federal/High Court completeness and counts not verified.
- **Machine access:** JavaScript application; document routes use `/article/{id}`. No anonymous search API or full judgment was verified. Free access exists alongside paid features; account requirements for the needed workflow remain untested.
- **Terms:** [Terms](https://jade.io/terms) grant a “non-exclusive, non-transferable, revocable licence” for specified research/professional uses. The linked [acceptable-use policy](https://jade.io/j/?c=acceptable+use+policy) produced an unreadable application shell; its automation conditions remain unknown.
- **Robots:** [robots.txt](https://jade.io/robots.txt): `Disallow: /search*`, `Disallow: /j/*`, `Disallow: /*.do`. Do not treat an accessible article route as authorization for automated search.
- **Status:** **VERIFIED:** terms and robots. **UNVERIFIED:** suitable anonymous machine workflow.

**3. Court websites — official; existing technical blockers remain.**

[High Court](https://www.hcourt.gov.au/) and [Federal Court judgments](https://www.judgments.fedcourt.gov.au/) remain the authoritative targets. Existing validation records Akamai/Cloudflare problems. This round, High Court robots timed out and Federal Court robots returned 403. No fresh successful judgment retrieval, terms clearance or reliable search protocol was established.

---

**`ie` — CASE LAW**

**None found meeting all requirements.**

- **Courts Service — official:** [Judgments portal](https://judgments.courts.ie/). Its [robots.txt](https://judgments.courts.ie/robots.txt) explicitly says `User-agent: *` / `Disallow: /`. **VERIFIED restriction.** No new usable machine route, document sample, coverage count or reuse licence established.
- **BAILII — LII:** [Homepage](https://www.bailii.org/), Irish court judgments among its collections; English. Its [copyright/terms page](https://www.bailii.org/bailii/copyright.html) and robots request encountered **Anubis Access Denied**. Search-indexed homepage text says: “BAILII's Terms of Service PROHIBIT bulk downloading, scraping, and the use of automated systems.” **UNVERIFIED by direct opening:** current full policy and document access. Not a cleared alternative.
- **IRLII — university initiative:** [IRLII](https://irlii.org/) opened, but a usable judgment collection, search protocol, coverage dates/count and reuse terms were not established. [robots.txt](https://irlii.org/robots.txt) returned 403. **VERIFIED homepage only; otherwise UNVERIFIED.**

---

**`in` — CASE LAW**

**1. Indian Supreme Court Judgments, AWS Open Data — other/open-data project; strongest unofficial lead.**

- **URL/coverage:** [AWS registry](https://registry.opendata.aws/indian-supreme-court-judgments/), maintained by Dattam Labs. Registry coverage is 1950–2025; the [repository](https://github.com/vanga/indian-supreme-court-judgments/blob/main/README.md) describes approximately 35,000 English judgments plus regional-language material and continuing updates. Counts/freshness were not independently audited.
- **Machine access:** Anonymous S3 ListObjectsV2 and individual objects. Pattern: `/data/pdf/year={YYYY}/english/{filename}.pdf`; JSON metadata is also documented. A prefix query with `max-keys=1` worked.
- **Sample:** [2025_10_131_151_EN.pdf](https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/data/pdf/year=2025/english/2025_10_131_151_EN.pdf) returned 200; **21 pages with extractable text**.
- **Terms:** Registry: “CC-BY-4.0” and “No AWS account required”. Repository explicitly states “individual PDF and JSON objects are also exposed for targeted access.”
- **Robots/blocks:** [Bucket robots.txt](https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/robots.txt) returned 404. No bot check, login or key encountered.
- **Status:** **VERIFIED:** licence declaration, anonymous listing and individual text PDF. **Important limitation:** S3 prefix listing is not full-text search. A broad keyword adapter would need an additional search service/index; do not silently introduce bulk ingestion.

**2. Indian High Court Judgments, AWS Open Data — other/open-data project; strong retrieval candidate.**

- **URL/coverage:** [AWS registry](https://registry.opendata.aws/indian-high-court-judgments/) and [dataset documentation](https://github.com/vanga/indian-high-court-judgments/blob/main/opendata/docs/dataset.md). Publisher reports **25 High Courts, 45 benches and approximately 17.8 million judgments**. English and regional-language documents; earliest coverage varies and was not established. Documentation and registry disagree on update frequency.
- **Machine access:** Anonymous S3; `/data/pdf/year={year}/court={code}/bench={id}/{filename}.pdf`, plus metadata. [Patna sample](https://indian-high-court-judgments.s3.ap-south-1.amazonaws.com/data/pdf/year=2025/court=10_8/bench=patnahcucisdb94/BRHC010000012025_1_2025-02-05.pdf) returned 200; **two pages with extractable text**. Other documents may differ.
- **Terms:** Registry declares “CC-BY-4.0” and “No AWS account required”.
- **Robots/blocks:** [Bucket robots.txt](https://indian-high-court-judgments.s3.ap-south-1.amazonaws.com/robots.txt) returned 404. No authentication or bot check encountered.
- **Status:** **VERIFIED:** anonymous listing, individual PDF and licence declaration. **UNVERIFIED:** corpus completeness, scan proportion and full-text search. Same retrieval-only limitation as above.

Both require the unofficial-source label. These findings do not remove the permission gate on the repository’s existing Indian route.

---

**`il` — CASE LAW**

**1. VERSA, Cardozo School of Law — university; accessible but permission unresolved.**

- **URL/coverage:** [VERSA](https://versa.cardozo.yu.edu/), selected Israeli Supreme Court judgments translated into English. Not comprehensive; total and earliest year not established.
- **Machine access:** HTML `/opinions/{slug}`. [Movement for Quality Government v. Knesset](https://versa.cardozo.yu.edu/opinions/movement-quality-government-israel-v-knesset) opened with substantial translated judgment text. Completeness of every opinion in the underlying case was not established. `/opinions` exposes a search form using `search_api_views_fulltext`; successful submitted search not verified.
- **Terms:** [VERSA terms](https://versa.cardozo.yu.edu/terms-and-conditions): “Please see the Terms and Conditions of Yeshiva University.” Its linked legacy PDF timed out. The [current university terms](https://www.yu.edu/website-terms-use) say “solely for your personal, noncommercial home use”; applicability to VERSA’s legacy link remains unresolved.
- **Robots:** [robots.txt](https://versa.cardozo.yu.edu/robots.txt): `Crawl-delay: 10`, `Disallow: /search/`, with additional Drupal exclusions. Opinion routes are not generally excluded.
- **Status:** **VERIFIED:** opinion HTML, robots and terms linkage. **UNVERIFIED:** permission for Fontes reuse. Not shortlisted as unrestricted.

The official Supreme Court route remains a known authorization/undertaking issue from prior validation; no replacement permission-free official workflow was verified. **None found fully cleared.**

---

**`dk` — CASE LAW**

**1. Domsdatabasen — official; application required.**

- **URL/coverage:** [Domsdatabasen](https://domsdatabasen.dk/), selected Danish court decisions, principally the modern collection launched in 2022; Danish. Current count and historical completeness not established.
- **Machine access:** Official API supports case/download and change workflows. Public documentation does not make it anonymous.
- **Terms/access:** [API guidance](https://domsdatabasen.dk/spoergsmaal-og-svar/api-adgang-til-domsdatabasen/) explicitly states: “Der skal ansøges om API-adgang til Domsdatabasen.” An application is required. The linked application specifies operating conditions; no application was submitted.
- **Robots:** [robots.txt](https://domsdatabasen.dk/robots.txt) returned 404.
- **Status:** **VERIFIED:** API application requirement. **UNVERIFIED:** authenticated API and document retrieval. Not eligible as a no-signup adapter.

Also checked [domsdata.dk’s description](https://domsdata.dk/om): it claims to republish judgments obtained through the official API. Direct homepage/robots requests returned 503; no reuse licence or established institutional provenance was verified. The Supreme Court website remains a prior blocked lead. **None found meeting all requirements.**

---

**`ar` — CASE LAW**

**1. JUBA, Supreme Court of Buenos Aires Province — official; strong technical candidate, terms unresolved.**

- **URL/coverage:** [Search](https://juba.scba.gov.ar/Buscar.aspx), **provincial, not national**. Its coverage notice specifies SCBA headnotes from 1984, selected appellate decisions from 1990, full SCBA civil/commercial judgments from 1986 and other subjects from 1996. Spanish; total unknown.
- **Machine access:** Ordinary ASP.NET form POST to `/Buscar.aspx`, retaining hidden state. Query field: `ctl00$cphMainContent$txtExpresionBusquedaRapida`; subject selector: `ctl00$cphMainContent$ddlMateria`. Submitting `contrato` with subject `Todos` returned results and full-judgment links.
- **Documents:** `/VerTextoCompleto.aspx?idFallo={id}` returns HTML. [Tonelli, B. 66.927, 31 May 2017](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=143376) returned a substantive full judgment directly.
- **Terms:** No reuse/automation/AI-TDM terms located in the inspected pages or targeted site searches; **no permission text available to quote**.
- **Robots/blocks:** [robots.txt](https://juba.scba.gov.ar/robots.txt) returned 404. No login, CAPTCHA or bot block encountered.
- **Status:** **VERIFIED:** keyword search and full-text HTML. **UNVERIFIED:** reuse conditions. Worth pursuing, but not labelled licence-cleared.

**Rejected national leads:** [SAIJ terms PDF](https://www.saij.gob.ar/docs-f/Reglamento_uso.pdf) downloaded, but its seven pages yielded no extractable text; prior validation records personal-use/deep-link restrictions, which were not independently re-quoted this round. [SAIJ robots](https://www.saij.gob.ar/robots.txt) includes `Disallow: /descarga-archivo` and `Disallow: /_pdf`. CSJN’s CAPTCHA remains a prior known blocker, not newly resolved.

---

**`cn` — LEGISLATION**

**1. Supreme People’s Court republications — official; narrow fallback.**

- **URL/coverage:** [Civil Code publication](https://www.court.gov.cn/zixun/xiangqing/233181.html), Chinese, published 1 June 2020. The page contains the enacted code through Article 1260. This verifies one important statute, **not a comprehensive consolidated legislation collection**.
- **Machine access:** Direct HTML `/zixun/xiangqing/{id}.html`; no legislation-specific search API verified. Requires discovered article URLs.
- **Terms:** Footer says “中华人民共和国最高人民法院 版权所有”. No substantive reuse, automation or AI/TDM policy located on the inspected page.
- **Robots/blocks:** [robots.txt](https://www.court.gov.cn/robots.txt) returns an HTML “page not found” page with HTTP 200, not a valid robots policy. Web-tool opening timed out, but direct Fontes-UA requests succeeded.
- **Status:** **VERIFIED:** complete sample-code HTML. **UNVERIFIED:** reuse terms, wider coverage and consolidation freshness.

**2. National Laws and Regulations Database, NPC — official; unsuitable automation policy.**

- **URL/coverage:** [FLK](https://flk.npc.gov.cn/), national laws and other legislative/regulatory categories, Chinese. Current count not verified.
- **Terms/robots:** [robots.txt](https://flk.npc.gov.cn/robots.txt) explicitly states: “禁止使用任何自动化工具、脚本、爬虫程序采集或复制网站数据”, followed by `User-agent: *` / `Disallow: /`. This prohibits automated collection/copying, not merely bulk training.
- **Machine access:** Previous research identified JSON search/detail and DOCX-download routes; they were not revalidated or used to circumvent the restriction.
- **Status:** **VERIFIED exclusion.** Not shortlisted.

Also checked NPC’s English delivery host, [en.npc.gov.cn.cdurl.cn](https://en.npc.gov.cn.cdurl.cn/): TLS hostname mismatch on the direct robots request; the Civil Code PDF failed through the web tool. [AsianLII China](https://www.asianlii.org/cn/) returned 403; terms unavailable. **No comprehensive cleared source found.**

---

**`sg` — LEGISLATION**

**1. Government eGazette — official; best new lead, enacted texts rather than consolidations.**

- **URLs/coverage:** [Government Gazette](https://www.egazette.gov.sg/), [catalogue](https://www.egazette.gov.sg/gazettes/), [FAQ](https://www.egazette.gov.sg/faq/). FAQ states September 1998–present coverage. Acts, subsidiary legislation, bills and other notices, English; total archive count unknown. Public access required no login.
- **Machine access:** Catalogue HTML works. Dedicated `/egazette-browse/` search is JavaScript-driven; its query/API protocol was not verified. Individual PDFs use paths such as `/2025/Legislative%20Supplements/Acts%20Supplement/03.pdf` on `assets.egazette.gov.sg`.
- **Sample:** [Electronic Gazette and Legislation Act 2025](https://assets.egazette.gov.sg/2025/Legislative%20Supplements/Acts%20Supplement/03.pdf) returned 200; **26 pages with extractable text**.
- **Terms:** [Terms, §11](https://www.egazette.gov.sg/terms-of-use/) expressly permit reproduction and automated extraction, subject to conditions including: “the extraction must not be carried out in an abusive or intrusive, or a deceptive, manner”. Attribution/permission notices, accuracy, no implied government affiliation, no disruption and no security circumvention are required. Linking/framing also has conditions. **No SSO-style time window appears here.**
- **Robots:** [Main robots](https://www.egazette.gov.sg/robots.txt): `Allow: /`, `Disallow: /search`. [Asset-host robots](https://assets.egazette.gov.sg/robots.txt) returned 403; its policy remains unresolved.
- **Status:** **VERIFIED:** catalogue, terms permitting automation, and individual text PDF. **UNVERIFIED:** complete live search protocol and asset-host robots. Strong next implementation target with those outstanding checks.

**2. Singapore Statutes Online — official government service; expressly unofficial consolidations, time-restricted automation.**

- **URL/coverage:** [SSO](https://sso.agc.gov.sg/): current/historical Acts, subsidiary legislation and published versions, English. Pre-1998 historical coverage is incomplete; total unknown. Government-operated does not mean its consolidated text is authoritative.
- **Machine access:** HTML statute routes such as `/Act/{identifier}` and `/SL/{identifier}`. No successful direct statute retrieval or search API verified in this round.
- **Terms:** Search-indexed [terms](https://sso.agc.gov.sg/Terms-of-Use) and [FAQ](https://sso.agc.gov.sg/FAQ) say: “the extraction must only be carried out during the hours of 3 a.m. to 7 a.m. (Singapore Time)”. Other reproduction, attribution and non-disruption conditions apply.
- **Robots/blocks:** Direct homepage, terms and [robots](https://sso.agc.gov.sg/robots.txt) returned 403; existing validation identifies CloudFront blocking.
- **Status:** **UNVERIFIED direct access/current full terms; restriction supported by current search-indexed official text.** Not suitable for unrestricted round-the-clock live requests.

[CommonLII Singapore](https://www.commonlii.org/sg/) returned 410; no usable alternative established there.

---

**`no` — LEGISLATION**

**1. Lovdata — other, nonprofit foundation; content reuse more permissive than Round 1 suggested, access still blocked.**

- **URL/coverage:** [Lovdata](https://lovdata.no/), current consolidated Norwegian acts and central regulations, plus Norsk Lovtidend. Norwegian; exact current totals and historical reach not established.
- **Machine access:** Individual HTML laws exist. Prior research identifies free API archive listing/download routes, but these are bulk-oriented; no free per-document API was verified in this round.
- **Terms:** [Current terms, §2.3](https://lovdata.no/artikkel/brukervilkar_for_lovdatas_tjenester/1324) expressly allow “fritt kopiere, bruke og dele” individual legislative documents under NLOD 2.0 conditions. They also state: “Massenedlasting og systematiske uttrekk er ikke tillatt.” **The current-legislation exception matters:** do not describe all Lovdata statutes as personal/noncommercial-only or automatically subject to every general AI restriction.
- **Robots:** Both [website robots](https://lovdata.no/robots.txt) and [API-host robots](https://api.lovdata.no/robots.txt) contain a wildcard `Disallow: /`; named search-engine exceptions do not authorize Fontes.
- **Status:** **VERIFIED:** current terms and robots. **UNVERIFIED:** compliant free live per-document route. No suitable adapter route established.

Also examined [lovverk on GitHub](https://github.com/bartoszkobylinski/lovverk): a personal mirror claiming 5,880 Markdown documents and NLOD provenance. Individual documents, freshness and institutional reliability were not validated; repository robots were not separately checked. Not recommending it as an established reputable substitute. **None found meeting all requirements.**

---

**`hu` — LEGISLATION**

**1. Magyar Közlöny — official; usable gazette fallback.**

- **URL/coverage:** [Magyar Közlöny](https://magyarkozlony.hu/), Hungarian enacted legislation and official notices, **not consolidated codes**. Year selector spans 1998–2026; archive completeness and total count not established.
- **Machine access:** GET `/?year={year}&month={month}&serial={issue}`; [2026 issue 167 search](https://magyarkozlony.hu/?year=2026&month=11&serial=167) returned the correct issue. A `content` keyword field also exists, but keyword submission was not tested.
- **Documents:** Record example: [`/dokumentumok/0a8ebe91d6dcba9c1a6242fb243adc9629c08168/megtekintes`](https://magyarkozlony.hu/dokumentumok/0a8ebe91d6dcba9c1a6242fb243adc9629c08168/megtekintes). Follow its `/hivatalos-lapok/{token}/dokumentumok/{hash}/letoltes` link. The issue PDF returned 200; **154 pages with extractable text**.
- **Terms:** [Imprint](https://magyarkozlony.hu/impresszum) and [legal background](https://magyarkozlony.hu/jogszabalyi-hatter) opened. Footer: “2026 © Miniszterelnökség”. No separate substantive reuse licence or automation/AI clause located; permission remains unconfirmed.
- **Robots:** [robots.txt](https://magyarkozlony.hu/robots.txt): `User-agent: *` followed by an empty `Disallow:`.
- **Status:** **VERIFIED:** issue search, text PDF and robots. No login/bot check encountered. **UNVERIFIED:** reuse conditions and older scan proportion.

**2. Nemzeti Jogszabálytár — official; consolidated but automation-restricted.**

- **URL/coverage:** [NJT](https://njt.jog.gov.hu/), consolidated Hungarian legislation and historical versions. Exact count and earliest coverage not established.
- **Machine access:** HTML `/jogszabaly/{identifier}` and ELI routes are known from existing research; no fresh successful document/search transaction verified.
- **Terms:** [Terms](https://jog.gov.hu/felhasznalasi-feltetelek) prohibit driving the search using “a szolgáltatás keresőjét sorozatos kérésekkel, automatákkal, humán interfész segítségével meghajtani”. Bulk/database-building restrictions also apply; commercial reuse requires written approval. Basic browsing is free; expanded features involve registration.
- **Robots:** [robots.txt](https://njt.jog.gov.hu/robots.txt) permits `/jogszabaly/*` but excludes search paths including `/search/*`. Document-path permission does not override the search terms.
- **Status:** **VERIFIED:** restrictive terms and robots. **UNVERIFIED:** a permitted anonymous machine-search route. Not shortlisted.

---

**Ranked shortlist across jurisdictions**

No broad source was verified end-to-end against **every** requested criterion. The strongest next adapters, with their remaining limits exposed, are:

| Rank | Source | Why pursue it | Remaining limitation |
|---|---|---|---|
| **1** | **India — Supreme Court AWS dataset** | CC BY 4.0; anonymous individual text PDFs; substantial historical coverage | Retrieval by object/key works; full-text search is absent |
| **2** | **Singapore — eGazette [OFFICIAL]** | Explicit automated-extraction permission; free text PDFs; substantial archive | Unconsolidated; search protocol and asset-host robots unresolved |
| **3** | **India — High Courts AWS dataset** | CC BY 4.0; anonymous individual PDFs; broad publisher-reported coverage | No keyword API; heterogeneous documents and freshness require care |
| **4** | **Argentina — JUBA [OFFICIAL]** | Working keyword search and full judgment HTML | Buenos Aires Province only; reuse terms not located |
| **5** | **Hungary — Magyar Közlöny [OFFICIAL]** | Working issue search, text PDFs, permissive robots | Gazette rather than consolidation; reuse terms unresolved |
| **6** | **Japan — IP High Court Grand Panel [OFFICIAL]** | Working static index and text PDFs; no judgment-path robots exclusion | Very small specialist subset; nationwide search remains down |
| **7** | **Italy — Constitutional Court [OFFICIAL]** | Working individual HTML judgments; explicitly licensed open datasets | Radware blocks discovery; live API unavailable; licence scope needs care |

The India sources should be labelled **“unofficial, check the official text.”** JUBA and Magyar Közlöny are technically promising, but absence of located terms should remain an explicit unresolved field—not become a claim that automated reuse is permitted.