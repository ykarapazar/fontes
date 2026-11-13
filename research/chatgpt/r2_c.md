**Fontes — Round 2 source research**  
**Checked: 7 November 2026. Repository left unchanged.**

The strongest leads are **Mongolia’s Legalinfo legislation search**, **Nigeria’s NIPC Acts collection**, and **Cambodia’s ECCC judgments**, although ECCC covers only that tribunal. Egypt has a useful **sector-specific official alternative at GAFI**, but I found no clearly superior comprehensive replacement for Manshurat.

I consulted the specified repository research and adapter notes before checking sources. Below, **VERIFIED** applies only to the stated observation—not automatically to coverage, extraction quality, or permission. “Web opened” and “direct Fontes request succeeded” are distinguished where they differ. All verification dates are **2026-11-07**.

I searched for personal-use restrictions, automation/scraping prohibitions, AI/TDM clauses, copyright conditions and licences. **Terms not found does not mean permission granted; permissive robots.txt is not a content licence.** No geographical blocking was established; failures below describe what actually occurred.

---

**af — Afghanistan — missing CASE LAW**

**None found usable.**

- **Supreme Court — official:** [supremecourt.gov.af](https://supremecourt.gov.af/). The homepage opened, but what I could establish was news, administrative material and judicial statistics, not a searchable full-judgment collection. Dari/Pashto; judgment count and date coverage **UNVERIFIED**. The adapter’s previously checked final-decision pages remain a known dead end; I did not establish a replacement document or search route.
- **Machine access:** HTML website; no functioning judgment API, full-text document pattern or PDF corpus verified.
- **Robots:** [robots.txt](https://supremecourt.gov.af/robots.txt) returned successfully. Relevant restriction: `Disallow: /search/`; it also excludes administrative paths. It is **not** a blanket prohibition.
- **Terms:** No applicable reuse/automation terms or open licence located; nothing authoritative to quote.
- **Status:** **VERIFIED homepage and robots only.** Full judgments **UNVERIFIED**. AsianLII did not yield a verified accessible Afghan judgment collection in this check.

---

**bt — Bhutan — missing CASE LAW**

**1. Royal Court of Justice judgment archive — official**  
[Judgments archive](https://judiciary.gov.bt/archive-content/judgments)

- **Coverage:** Small mixed archive: ten displayed entries, including reports, press material and language variants—not ten distinct judgments. English and Dzongkha. A **2017 High Court preliminary order in DNT v PDP** was verified; complete date range and distinct judgment count are unknown.
- **Machine access:** HTML listing with direct `/archives/{filename}.pdf` links; no API verified. [DNT v PDP PDF](https://judiciary.gov.bt/archives/1697536320-.pdf) opened as a **23-page text-readable PDF**.
- **Metadata problem:** The link labelled “OAG (Government) v Opposition Party” led to an [11-page dissent concerning OAG v Tashi Commercial Corporation](https://judiciary.gov.bt/archives/1697606011-.pdf). An adapter must validate titles against document contents.
- **Terms:** No applicable terms/licence located on the inspected archive or through focused searching.
- **Robots:** [robots.txt](https://judiciary.gov.bt/robots.txt) timed out; **UNVERIFIED**, no quote available.
- **Blocks/status:** **VERIFIED through web opening:** archive and two PDFs. Direct-policy request timed out. No login encountered. Useful small collection, but robots and reuse remain unresolved.

---

**hk — Hong Kong — missing CASE LAW**

**1. HKLII — LII/university; unsuitable without permission**  
[HKLII](https://www.hklii.hk/) · [Legal information and conditions](https://www.hklii.hk/legal)

- **Coverage:** Hong Kong case-law collection; exact current court list, years and count were **not independently verified** because the live pages exposed only the JavaScript shell.
- **Machine access:** No working public search/document API verified. Do not treat the internal API as an available integration.
- **Robots:** [robots.txt](https://www.hklii.hk/robots.txt) returned: `User-agent: *` and `Disallow: /api`.
- **Terms:** The search-indexed version of its legal page says: **“HKLII specifically blocks all spiders and other automated agents from accessing its case-law via the Robots Exclusion Standard.”** The indexed conditions also describe personal reading/printing/copying and rights in added material.
- **Verification qualification:** That quotation is **search-index evidence**. Opening `/legal` directly returned a shell, so the current complete terms body is **UNVERIFIED**.
- **Conclusion:** **None found cleared for Fontes.** HKLII’s indexed express automation restriction is a substantive obstacle. The Judiciary/Legal Reference source already rejected in the repository for robots restrictions remains an excluded alternative.

---

**id — Indonesia — missing CASE LAW**

**1. Supreme Court, Direktori Putusan — official; substantial but direct access blocked**  
[Judgment directory](https://putusan3.mahkamahagung.go.id/direktori.html)

- **Coverage:** Supreme Court and general, religious, military, administrative and tax courts; Indonesian. The opened directory displayed **millions of records**, including approximately **275,000 Supreme Court** and **7.6 million religious-court** entries. These are website counters, not audited unique-judgment totals. Listings included 2026 decisions.
- **Machine access:** HTML directory and filters, including the observed [2026 decision-year route](https://putusan3.mahkamahagung.go.id/direktori/index/tahunjenis/putus/tahun/2026.html). The linked search endpoint is [`/search.html`](https://putusan3.mahkamahagung.go.id/search.html), but it returned **403**. No successful full-document download or API verified in this round.
- **Robots changed since the repository checks:** [robots.txt](https://putusan3.mahkamahagung.go.id/robots.txt) now contains:
  `User-agent: *`  
  `Content-Signal: search=yes,ai-train=no,use=reference`  
  `Allow: /`
  
  Several named AI/training agents have separate prohibitions. The previous generic blanket-disallow finding should not be repeated as current.
- **Terms:** Directory footer: **“Hak Cipta dan Kekayaan Intelektual dilindungi Undang-Undang.”** Copyright and intellectual property are protected by law. The linked [about page](https://putusan3.mahkamahagung.go.id/tentang.html) returned **429**; no complete reuse terms verified.
- **Blocks/status:** **VERIFIED directory through web opening and robots directly.** The same directory returned **403 to Fontes**. Search returned 403; about returned 429. Promising source, **not presently a verified working adapter target**.

---

**iq — Iraq — missing CASE LAW**

**None found usable.**

1. **Federal Supreme Court — official:** [iraqfsc.iq](https://www.iraqfsc.iq/).
2. **Higher Judicial Council — official:** [hjc.iq](https://www.hjc.iq/).

Both fresh homepage checks returned **403**. Their [Federal Supreme Court robots](https://iraqfsc.iq/robots.txt) and [HJC robots](https://www.hjc.iq/robots.txt) also returned 403, so no rules could be quoted. Terms could not be inspected.

Arabic decisions are the intended material, but current full-text availability, years, counts, formats and machine routes are **UNVERIFIED**. The Iraqi legal-database redirects/WAF failures recorded in `research/iq.md` remain additional known dead ends; no working replacement was established. A search result advertising a demonstrative/mock judgment service was excluded.

---

**kh — Cambodia — missing CASE LAW**

**1. Extraordinary Chambers in the Courts of Cambodia — official hybrid tribunal**  
[ECCC](https://www.eccc.gov.kh/en)

- **Coverage:** ECCC proceedings only—not Cambodia’s ordinary Supreme Court or general domestic case law. Khmer and English documents verified; other-language coverage and aggregate judgment count were not audited.
- **Machine access:** Public PDF links under `/sites/default/files/documents/`. **Direct Fontes download succeeded** for [Case 001 appeal judgment, F28, 3 February 2012](https://www.eccc.gov.kh/sites/default/files/documents/F28_EN.PDF): **350 pages, approximately 21.6 MB**, with extractable English text. The text shows OCR artefacts; this is not evidence that every file has clean native text. No current search API verified.
- **Robots:** [robots.txt](https://www.eccc.gov.kh/robots.txt) returned only `User-agent: *`, with no disallow directives.
- **Terms/access policy:** The [Practice Direction on Classification and Management of Case-Related Information](https://www.eccc.gov.kh/sites/default/files/legal-documents/6-PD%20on%20Classification%20EN%20Rev2%20.pdf), article 12.3, states: **“Materials classified as public may be accessed by the public.”** It separately preserves restrictions affecting third-party copyrighted/agreement-covered materials. This is an access rule, **not a blanket redistribution licence**. No general automation or AI/TDM policy located.
- **Blocks/status:** **VERIFIED homepage, policy, robots and one full judgment.** The web reader rejected the large judgment by size; direct retrieval worked without login. Some legacy page routes fail.
- **Conclusion:** Good narrowly scoped candidate. Ordinary Cambodian case law: **none found usable**; the constitutional/Supreme Court and archive failures documented in round 1 were not replaced by a verified broad corpus.

---

**la — Laos — missing CASE LAW**

**None found usable.**

- **People’s Supreme Court — official:** [peoplecourt.gov.la/la/](https://www.peoplecourt.gov.la/la/), also identified by the [Library of Congress Laos judicial guide](https://guides.loc.gov/law-laos/judicial).
- **Access:** Website could not be opened; the direct [robots request](https://www.peoplecourt.gov.la/robots.txt) failed DNS resolution. The alternative `spc.gov.la` failure is already recorded in the repository.
- **Coverage/machine access:** No verified judgment corpus, search route, API, document format, year range or count. Lao would be expected, but document-level language was not verified.
- **Terms:** Inaccessible/not located; no quote available.
- **Status:** **UNVERIFIED as a usable source.** No working LII/university replacement established.

---

**mv — Maldives — missing CASE LAW**

**1. Supreme Court judgment registry — official; metadata works, full documents blocked**  
[Judgments](https://www.supremecourt.mv/case-registry/judgments)

- **Coverage:** Registry displayed **703 judgments**, including **4 November 2026**. Dhivehi with English metadata/summaries. Earliest coverage was not established.
- **Machine access:** HTML listing; records use `/case-registry/judgments/{uuid}`. [Adam Iyaz v Dhivehi Fuluhunge Khidhumaiy, [2026] SC 43](https://www.supremecourt.mv/case-registry/judgments/80e8cfd1-49b5-4ce5-9bd4-1a402dcb1e5c) opened with a summary and citation.
- **Document problem:** Its actual [judgment PDF link](https://old.supremecourt.mv/storage/mv/sc-ninmunthah/hukum/hukum-2023-sc-a-06iyaz.pdf) returned **403**. Thus full-text extraction remains **UNVERIFIED**; a summary is not the judgment.
- **Robots:** [robots.txt](https://supremecourt.mv/robots.txt) returned `Allow: /`, with exclusions for `/admin`, `/api/admin` and `/auth`.
- **Terms:** Footer reserves rights; no applicable licence or automation/AI terms located. No separate policy body was verified.
- **Blocks/status:** **VERIFIED registry, sample metadata and robots.** Legacy document host remains blocked, consistent with the earlier Cloudflare finding. High Court/DJA failures in `research/mv.md` remain known alternatives, not newly verified working sources.
- **Conclusion:** Worth revisiting only when the official full-document path becomes accessible.

---

**et — Ethiopia — missing CASE LAW**

**None found meeting the no-login and verified-access requirements.**

**1. AbyssiniaLaw cassation collection — other/private legal information portal**  
[Cassation volumes](https://abyssinialaw.com/decisions/federal-supreme-court-cassation-decisions?layout=table&start=0)

- **Coverage:** Index lists Federal Supreme Court cassation **volumes 1–28**, principally Amharic. These are volumes, not 28 judgments. Years, total decisions and PDF extraction quality were not verified.
- **Machine access:** HTML index with volume detail and `/download` links. The sampled [volume 28 download](https://abyssinialaw.com/decisions/federal-supreme-court-cassation-decisions/federal-supreme-court-cassation-decision-volume-28/download) **redirected to login**. No signup attempted; whether access requires payment was not established.
- **Robots:** [robots.txt](https://abyssinialaw.com/robots.txt) includes `Disallow: /uploads/` and `Disallow: /media/`, plus other application paths.
- **Terms:** Footer says **“All Rights Reserved.”** No reuse terms located. The linked [privacy policy](https://abyssinialaw.com/who-are-we/privacy-policy) returned 502.
- **Status:** **VERIFIED catalogue and login requirement for the sampled download.** Not a no-login candidate.

**2. LawEthiopia — other/private legal information portal**  
[Individual cassation decisions](https://lawethiopia.com/case-law.html) · [Cassation reports](https://lawethiopia.com/index.php/case-law/case-reports-cassation)

- **Coverage/access:** Individual case headings and volume listings opened; Amharic case material with English subject headings. Complete years/count and underlying PDF quality **UNVERIFIED**. HTML title filtering exists; no API verified.
- **Robots:** [robots.txt](https://lawethiopia.com/robots.txt) explicitly includes `User-agent: ChatGPT-User` with `Disallow: /`; other named AI agents are similarly excluded. The generic group has `Crawl-delay: 5` and path restrictions.
- **Terms:** No applicable reuse licence/terms located. Fontes is not explicitly named, but the named-agent restrictions should not be presented as affirmative permission for an AI-connected replacement client.
- **Status:** **VERIFIED index and robots only.** Do not shortlist without clarification.

**Official source checked:** [fsc.gov.et](https://fsc.gov.et/) and its robots endpoint returned **404** in the fresh direct checks. `ethiolii.org` failed DNS; no working EthioLII collection was verified.

---

**ly — Libya — missing CASE LAW**

**1. Libyan Supreme Court — official; partial content**  
[Sample constitutional decision page](https://alolya.gov.ly/article/4b695a55-3fb9-44b6-bc68-51b8b2348081?from=/)

- **Coverage:** Arabic constitutional decision metadata and legal principles opened. The sample concerns appeal **12/70**. Overall years and count unknown.
- **Machine access:** HTML `/article/{uuid}` pages expose principles. Full reasons/disposition were not verified; the page’s tabs must not be assumed to contain retrievable full judgments.
- **Robots:** [robots.txt](https://alolya.gov.ly/robots.txt): `Disallow: /api/` and `Disallow: /pdf-viewer`, alongside a general allow.
- **Terms:** Footer: **“ﺟﻤﻴﻊ الحقوق ﻣﺤﻔﻮﻇﺔ”**—all rights reserved. No broader reuse licence or AI/TDM terms located.
- **Status:** **VERIFIED partial HTML and robots; full judgment UNVERIFIED.** Do not implement through the prohibited API/viewer routes.

**2. Libyan Law Society — other/nonprofit legal archive; terms prevent an unrestricted recommendation**  
[lawsociety.ly](https://lawsociety.ly/)

- **Coverage:** Homepage displayed **2,117 judgments**. Arabic; archive-wide historical dates should not be mistaken for the judgment collection’s verified date range.
- **Machine access:** Full HTML judgment text opened. The site provides `/ruling/{slug}/` pages and AKN links, including [constitutional judgment 12/2026](https://lawsociety.ly/akn/ly/judgment/sc-constitutional/2026/12).
- **Robots:** [robots.txt](https://lawsociety.ly/robots.txt) includes `Crawl-delay: 2`, `Allow: /akn/`, and signals `ai-train=no`, `search=yes`, `ai-input=yes`. It allows the document endpoint while restricting other `/wp-json/ls/` routes.
- **Terms:** [Terms of use](https://lawsociety.ly/about/terms-of-use/) prohibit **“استخدام أدوات أو برامج آلية لاستخراج أو نسخ المحتوى أو البيانات بشكل منهجي من الموقع.”** This prohibits systematic automated extraction/copying. They also reserve rights in transcription, formatting and metadata and require prior written permission for specified reuse.
- **Status:** **VERIFIED full HTML sample, robots and terms.** The favourable AI-input signal does **not** remove the contractual restrictions. Not cleared for Fontes’s general operation.

---

**eg — Egypt — missing LEGISLATION**

**No comprehensive, clearly reusable improvement over Manshurat was found. There is a useful narrower official source.**

**1. GAFI Virtual Library — official; investment/company-law subset**  
[Current virtual library](https://gafi.gov.eg/en/booklet)

- **Coverage:** **17 library results overall**, mostly guides—not 17 statutes. Visible legal titles include Companies Law **159/1981** and Investment Law **72/2017**, advertised in three and seven languages respectively. Arabic document verified.
- **Machine access:** HTML catalogue; linked PDFs under `gafiadmin.gafi.gov.eg/style-library/ExtractedVirtualLibraries/...`. The [132-page Companies Law PDF](https://gafiadmin.gafi.gov.eg/style-library/ExtractedVirtualLibraries/4084/897801cd5c4144f2a2810019c5f80e88/CompaniesLaw159_AR/CompaniesLaw159_AR.pdf) opened with substantial extractable Arabic text, although some headings are garbled. It identifies amendments through **2018**; currency through 2026 is not established. No public search API verified.
- **Important migration correction:** Search engines still expose readable old GAFI PDFs. A direct request to the old English Investment Law URL instead returned an **HTML 404 page with HTTP 200**. Use current catalogue links, not indexed legacy routes.
- **Robots:** [Main-site robots](https://gafi.gov.eg/robots.txt): `User-agent: *` / `Allow: /`. [PDF-host robots](https://gafiadmin.gafi.gov.eg/robots.txt) returned **404**.
- **Terms:** Current footer says **“Copyright © August 2026 Egypt is Paving the Way - GAFI.”** No applicable reuse/automation licence located. The Companies Law edition says the Official Gazette prevails if its reference copy differs.
- **Status:** **VERIFIED current catalogue, web-readable sample and robots responses.** Narrow alternative with extraction and currency limitations; no login encountered.

**2. Manshurat — university-supported/nonprofit legal archive**  
[manshurat.org](https://manshurat.org/)

- **Coverage:** Broad Arabic legislation and other legal materials, with recent items through 2025 visible. Exact statute count unknown. The repository’s finding of mixed HTML and scanned documents remains valid; no uniform text corpus established.
- **Machine access:** HTML `/node/{id}` records and attachments. No usable public API verified.
- **Robots:** [robots.txt](https://manshurat.org/robots.txt) says `Crawl-delay: 10` and `Disallow: /search/`, including the corresponding query-string search route.
- **Terms:** [Copyright/conditions page](https://manshurat.org/node/21612): **“Requests for permission to quote or use any content should be addressed to the author(s) directly.”** This is not a blanket open licence; its application to underlying public legal texts versus contributed material needs resolving.
- **Status:** **VERIFIED homepage, terms and robots.** Not cleared as an unrestricted automated source.

**3. National Investment Bank legal library — official; weaker extraction**  
[General laws](https://www.nib.gov.eg/English/LIBRARY-E/general-laws-e.html)

- **Coverage:** Approximately **139 document links**, including duplicates/regulations, spanning older legislation into the 2020s; primarily Arabic despite English labels. Not a comprehensive consolidated code collection.
- **Machine access:** HTML listing → `/PDF/{filename}.pdf`. The sampled Investment Law PDF opened, but Arabic extraction was badly garbled.
- **Terms:** Footer: **“Copyright reserved for NIB.”** No separate reuse/automation policy located.
- **Robots:** [robots.txt](https://www.nib.gov.eg/robots.txt) returned **404**.
- **Status:** **VERIFIED listing and sample; not a better text source.**

Also checked: the Parliamentary Affairs legislation portal returned 502 through the web tool and a certificate-verification failure directly; the Labour Ministry legislation page did not yield a working replacement.

---

**ng — Nigeria — missing LEGISLATION**

**1. Nigerian Investment Promotion Commission Acts collection — official; best new Nigerian lead**  
[Acts catalogue](https://nipc.gov.ng/external-resources/document-types/act)

- **Coverage:** Selected business, investment, tax, labour, power and related Acts. English; historical legislation and **2025 Acts**. Fifteen cards on the first page and three catalogue pages suggest roughly **30–45 records**, not an audited count. Not a complete consolidated Laws of the Federation.
- **Machine access:** HTML catalogue with `?page=2` pagination; metadata under `/external-resources/{slug}`; PDFs under `/assets/resources/{slug}/{filename}.pdf`. [Nigeria Revenue Service Act 2025](https://nipc.gov.ng/assets/resources/nigeria-revenue-service-establishment-act-2025/nigeria-revenue-service-establishment-act-2025-gazette.pdf) downloaded directly with Fontes: **32 pages, readable text**. The [Joint Revenue Board Act 2025](https://nipc.gov.ng/assets/resources/joint-revenue-board-establishment-act-2025/joint-revenue-board-establishment-act-2025-gazette.pdf) also opened as text.
- **Robots:** [robots.txt](https://nipc.gov.ng/robots.txt): `User-agent: *` / `Disallow:`—empty restriction.
- **Terms:** Footer reserves all rights. No applicable terms granting reuse, restricting automated access or addressing AI/TDM were located. No open licence established.
- **Status:** **VERIFIED catalogue, direct PDF access and robots.** No login/key/challenge encountered. Strong technical candidate, with reuse policy unresolved.

**2. National Assembly — official; current Acts, weak catalogue**  
[nass.gov.ng](https://nass.gov.ng/)

- **Coverage:** Recent legislation. The [Electoral Act 2026](https://nass.gov.ng/documents/download/11248) opened as a **121-page English text PDF**. Other homepage titles include Bills, so document status must be checked individually.
- **Machine access:** Direct `/documents/download/{id}` links work for the sample. The linked [Acts listing](https://nass.gov.ng/documents/magazine) opened with an empty table; no functioning search/API established.
- **Robots:** [robots.txt](https://nass.gov.ng/robots.txt) returned HTML rather than a robots file.
- **Terms:** Footer’s Terms/Privacy links were placeholders, not accessible policy documents. Copyright notice present; no reuse/automation terms verified.
- **Status:** **VERIFIED sample PDF, not a dependable complete catalogue.** No login encountered.

**3. NigeriaLII — LII; reject under current policies**  
[NigeriaLII terms](https://nigerialii.org/terms-of-use/)

- **Coverage:** Legislation and other legal materials; current legislative count/date coverage was not audited because policy already prevents recommendation.
- **Terms:** **“Scraping and bulk downloading from this website is strictly prohibited.”** The page also identifies **“Creative Commons Attribution-NonCommercial 4.0 International”** conditions. Terms were readable directly, although the web tool returned 403.
- **Robots:** [robots.txt](https://nigerialii.org/robots.txt) includes `Content-Signal: ai-train=no, search=yes, ai-input=no`, plus restricted API/search/content paths.
- **Status:** **VERIFIED restrictive policies.** “No training” does not address its separate **AI-input prohibition**. No API/document integration recommended.

PLAC remains a historical fallback **frozen at 31 December 2002**, not a current consolidated 2004/2026 collection.

---

**jo — Jordan — missing LEGISLATION**

**1. Prime Ministry Official Gazette — official; current enactments, not consolidated**  
[Gazette index](https://www.pm.gov.jo/ar/Pages/NewsPaper)

- **Coverage:** Arabic gazette issues; the index showed **146 pages of ten issues**, including issue **6086, 5 November 2026**. This is an approximate issue-list size, not a count of statutes.
- **Machine access:** HTML issue pages, e.g. [issue 6086](https://www.pm.gov.jo/Ar/Pages/NewsPaperDetails/6086), link to a DocuWare viewer at `doc.pm.gov.jo/DWWebClient/Integration.aspx`. The viewer opened as an application shell; full PDF/text extraction was **not verified**. No API verified.
- **Robots:** Both [main-site robots](https://www.pm.gov.jo/robots.txt) and [document-host robots](https://doc.pm.gov.jo/robots.txt) returned **404**.
- **Terms:** [Copyright conditions](https://www.pm.gov.jo/AR/Pages/حقوق_النشر) allow **“للاستخدام الشخصي أو للاستخدام داخل المؤسسة ولإغراض غير تجارية.”** That is personal/internal institutional, noncommercial use. Further conditions limit reproduction and require permission for other uses. [Terms of use](https://www.pm.gov.jo/AR/Pages/شروط_الاستخدام) prohibit unauthorized access and disruptive/overloading activity; no blanket automation or AI clause was found in the inspected text.
- **Status:** **VERIFIED index and terms; document extraction UNVERIFIED.** No login needed for the index.

**Consolidated legislation: none found usable.** The Legislation and Opinion Bureau’s encrypted delivery is already documented in the repository; I did not reverse it or suggest bypassing it.

---

**kg — Kyrgyzstan — missing LEGISLATION**

**1. Ministry of Justice Central Legal Database — official; access unresolved**  
[cbd.minjust.gov.kg](https://cbd.minjust.gov.kg/)

- **Coverage:** Kyrgyz/Russian legislation and editions. Current count and full date range **UNVERIFIED**. Search indexing exposes specific editions, but that does not prove successful retrieval.
- **Machine access:** Observed routes include [document search](https://cbd.minjust.gov.kg/search-docs/ru) and [Civil Code edition](https://cbd.minjust.gov.kg/4/edition/57538/ru). Opening exposed the application shell, not verified full statute text. No public API verified.
- **Robots:** [robots.txt](https://cbd.minjust.gov.kg/robots.txt) dropped the direct connection.
- **Terms:** No accessible complete terms/licence established. An “open data” label in search results is not sufficient licence evidence.
- **Status:** **UNVERIFIED for usable full-text access**, consistent with the adapter’s connection problems.

**2. FAOLEX — other/intergovernmental repository; selected fallback**  
[Kyrgyzstan profile](https://faolex.fao.org/countries/KGZ) · [Civil Code record](https://faolex.fao.org/en/documents/LEX-FAOC219736/civil-code-of-the-kyrgyz-republic-kgz-1996)

- **Coverage:** Selected legislation, particularly FAO-related sectors, plus some general codes. Russian and selected English translations. Total count unknown.
- **Machine access:** Record pages `/en/documents/{record-id}/{slug}` and PDFs `/docs/pdf/{filename}.pdf`. The [English Civil Code PDF](https://faolex.fao.org/docs/pdf/kyr219736.pdf) opened with **249 text-readable pages**, but its stated amendments reach **1997**—not a current consolidated code.
- **Robots:** [robots.txt](https://faolex.fao.org/robots.txt) excludes `/?filters=` and `/design-system/`; no restriction on the sampled PDF route.
- **Terms:** [FAO terms](https://www.fao.org/contact-us/terms/en/) permit specified attributed use, including **“for use in non-commercial products or services”**; commercial use/adaptations and third-party material require additional attention. No blanket AI/automation ban found in that page.
- **Status:** **VERIFIED sample text and policies.** Country-page rendering was not useful. A limited, version-sensitive fallback—not a substitute for current Ministry consolidation.

---

**mn — Mongolia — missing LEGISLATION**

**1. Legalinfo — official; strongest broad legislation lead**  
[legalinfo.mn](https://legalinfo.mn/)

- **Existing adapter:** `mn.py` covers case law, so adding Legalinfo legislation would fill the missing half rather than duplicate existing coverage.
- **Coverage:** Mongolian laws and subordinate instruments, with selected English translations. The inspected interface displayed **956 laws**, alongside other instrument categories. This is the site’s category counter, not an independently audited number of current consolidated statutes.
- **Machine access:** **Direct Fontes POST succeeded** to `https://legalinfo.mn/mn/ajaxList/` using form fields `title` and `isvalid=1`; response was JSON containing HTML results. Documents use `/mn/detail?lawId={id}` and some `/mn/detail/{id}` routes. [Example English law page](https://legalinfo.mn/mn/detail/15789) opened with full HTML text; it labels the translation unofficial.
- **Robots:** [robots.txt](https://legalinfo.mn/robots.txt) returned **404**.
- **Terms:** The [site-rules page](https://legalinfo.mn/mn/about/16106883680221) links an embedded [policy PDF](https://legalinfo.mn/storage/uploads/process/202602/file_1770627213602915_163403209487511.pdf). The PDF could not be read in this round; web retrieval returned 403. Therefore its automation/AI/reuse clauses are **UNVERIFIED**. Footer: **“Бүх эрх хуулиар хамгаалагдсан.”** All rights protected by law.
- **Status:** **VERIFIED search endpoint and HTML document access without login.** Terms remain the principal unresolved gate. Do not repeat the earlier claim that Legalinfo is simply inaccessible.

---

**np — Nepal — missing LEGISLATION**

**1. Nepal Law Commission — official; catalogue works, document extraction remains problematic**  
[Alphabetical Acts index](https://lawcommission.gov.np/pages/alphabetical-index-of-acts/) · [Volume index](https://lawcommission.gov.np/pages/list-volume-act/)

- **Coverage:** Broad Nepali Acts catalogue organised into **17 subject volumes**, including recent entries. Exact distinct statute count and consolidation dates were not audited. English material exists separately, but its completeness was not established.
- **Machine access:** HTML alphabetical index links to subject volumes/documents. An indexed search route uses `/search/?page=1&q={query}`; search-result usefulness was not independently verified. Current attachments use government CDN hosts; the repository records damaged legacy-font extraction and intermittent failures.
- **Legacy host:** [repository.lawcommission.gov.np](https://repository.lawcommission.gov.np/) timed out; do not present old HTML statute routes as working.
- **Robots:** [robots.txt](https://lawcommission.gov.np/robots.txt) returned `User-agent: *` and `Crawl-delay: 10`.
- **Terms:** No applicable reuse licence or automation/AI policy located; no terms quotation available.
- **Status:** **VERIFIED current HTML index and robots.** A reliable current full-text document workflow remains **UNVERIFIED**.

**2. FAOLEX — other/intergovernmental repository; useful English-document fallback**  
[National Civil Code 2017 PDF](https://faolex.fao.org/docs/pdf/nep209663.pdf)

- **Coverage:** The sampled English National Civil Code; broader Nepal coverage and current amendment completeness not audited.
- **Machine access:** **Direct Fontes download succeeded:** approximately **13.4 MB, 404 pages**, with readable English text. The web reader failed its size limit, which was not a source-access block.
- **Robots/terms:** Same [FAOLEX robots](https://faolex.fao.org/robots.txt) and [FAO terms](https://www.fao.org/contact-us/terms/en/) described under `kg`: document path not excluded; attributed noncommercial use permitted subject to exceptions/third-party rights. Free software alone does not make every downstream use noncommercial.
- **Status:** **VERIFIED full sample and policies.** Useful supplement, not a comprehensive current consolidated Nepal adapter.

---

**Ranked next-adapter shortlist**

No candidate was verified against **every** requested criterion with both dependable full-text access and fully resolved reuse terms. The ranking therefore distinguishes implementation leads from cleared deployment recommendations.

| Rank | Jurisdiction/source | Why it merits the next work | Remaining gate |
|---:|---|---|---|
| **1** | **mn — Legalinfo — OFFICIAL** | Broad legislation coverage; working direct search; full HTML documents; no login | Read and assess the linked site-rules PDF |
| **2** | **ng — NIPC — OFFICIAL** | Working catalogue; readable recent Acts; direct Fontes downloads; unrestricted generic robots | Limited subject coverage; no affirmative reuse licence located |
| **3** | **kh — ECCC — OFFICIAL** | Direct public judgments; no login; no robots disallow; extractable text | Tribunal-only scope; OCR quality; general reuse policy unresolved |
| **4** | **ng — National Assembly — OFFICIAL** | Verified readable Electoral Act 2026 PDF | Empty Acts catalogue; ineffective policy links; discovery reliability |
| **5** | **eg — GAFI — OFFICIAL** | Current library links and readable company-law material; generic robots allow | Narrow coverage, partial text corruption, edition currency and reuse terms |
| **6** | **bt — Judiciary — OFFICIAL** | Small accessible collection of text-readable judgments/orders | Robots timeout, missing terms and a verified metadata mismatch |

**Conditional supplementary source:** FAOLEX for `np` and `kg`, where the individual edition is suitable and its noncommercial/third-party conditions fit the deployment.

**Do not promote yet:** `id` needs direct access restored; `mv` needs reachable full judgments; `hk`, NigeriaLII and Libyan Law Society have substantive policy obstacles; `af`, `iq` and `la` produced no usable verified corpus.