# Fontes source research: Asia, Middle East and Pacific

**Checked: 6 November 2026.** Coverage: **46 jurisdictions, 75 missing halves**. Repository research, including `research/SIGNUPS.md` and the relevant country/region files, was read before web research. No files were changed, accounts created, or access controls bypassed.

**Verification labels**

- **VERIFIED—text:** opened an actual document and obtained its text.
- **VERIFIED—index:** opened a working catalogue; document retrieval remains unverified unless stated.
- **UNVERIFIED:** search-index evidence, an application shell, an inaccessible source, or a finding retained from repository research.
- All verification dates below are **2026-11-06**. Counts and coverage are **unknown unless explicitly stated**. A sample document does not establish completeness.
- “Terms not found” means **no quotable terms were located**, not unrestricted permission. A missing robots.txt is not a copyright licence.
- Unless specified, **no JSON/XML API was verified**. Anonymous access was established only for the pages/documents successfully opened.
- Timeouts and 403 responses are reported as observed; **geo-blocking and frequent downtime were not established**.

## Shared Pacific LII finding

**PacLII — LII, not an official publisher:** [PacLII](https://www.paclii.org/).

Country pages remain plausible fallbacks, but document access failed in these checks: direct requests encountered 403 responses; the web-fetch tool sometimes reported 410 or fetch failures. Earlier repository research identifies Cloudflare challenges. **UNVERIFIED as a usable document source.**

Its [robots.txt](https://www.paclii.org/robots.txt) did open:

> `User-agent: *`  
> `Content-Signal: search=yes,ai-train=no,use=reference`  
> `Allow: /`

Named training crawlers are separately disallowed. This is **not an explicit grant for feeding complete documents into an MCP/LLM workflow**; `use=reference` needs consideration. Separate terms were not successfully verified. Country coverage, document formats and counts were not revalidated behind the access failures.

## Jurisdictions needing both halves

### ae — United Arab Emirates, federal

- **legislation — official:** [UAE Legislation](https://uaelegislation.gov.ae/en). Federal constitution, laws, decree-laws and regulations; Arabic and English. Indexed documents use `/en/legislations/{id}/download`, apparently PDF; [constitution](https://uaelegislation.gov.ae/en/constitution) also has indexed HTML. **UNVERIFIED working access:** constitution returned **403**; prior research identified Cloudflare. [Robots](https://uaelegislation.gov.ae/robots.txt): `"User-agent: *"` and empty `"Disallow:"`. Terms and any account requirements could not be verified.
- **caselaw — official:** [MoJ Court Judgments](https://www.moj.gov.ae/en/laws-and-legislation/court-judgments.aspx). Intended federal judgment source; Arabic/English interface. **UNVERIFIED:** page and [robots](https://www.moj.gov.ae/robots.txt) returned `"The requested URL was rejected."` No working search, document route or terms verified.
- **Result:** none found usable for **federal** case law. DIFC and ADGM were deliberately excluded because they do not fill this federal gap.

### bn — Brunei

- **legislation — official:** [AGC BRULAW](https://www.agc.gov.bn/services_brulaw-2/). **VERIFIED—index.** Alphabetical laws and new legislation, including 2026; Malay/English. The current site uses WordPress, with PDFs under `/wp-content/uploads/YYYY/MM/`. A linked [2026 PDF](https://www.agc.gov.bn/wp-content/uploads/2026/07/S-7_2026-E.pdf) could not be opened by the web tool; its text layer is **unverified**. [Robots](https://www.agc.gov.bn/robots.txt): **404**. Terms not found.
- **caselaw — official:** [Judiciary judgments](https://www.judiciary.gov.bn/judgments/). **VERIFIED—text:** [OS 10/2026 judgment](https://www.judiciary.gov.bn/wp-content/uploads/2026/10/judgment_OS_10_2026.pdf), a six-page text PDF. Court of Appeal, High Court and Intermediate Court material; English. Index includes older cases, including 2017; complete range unknown. Pagination uses `/judgments/page/2/?et_blog`; search parameters not verified. [Robots](https://www.judiciary.gov.bn/robots.txt): **404**. Footer says `"All Right Reserved."`; substantive terms were not located. No login encountered.

### fj — Fiji

- **legislation — official:** [Parliament Acts](https://www.parliament.gov.fj/acts/). **VERIFIED—index.** Annual enacted Acts, **2014–2026**, English; linked PDFs under `/wp-content/uploads/`. Consolidated law coverage and PDF text layers not verified. [Robots](https://www.parliament.gov.fj/robots.txt): `"Disallow: /wp-admin/"`, `"Allow: /wp-admin/admin-ajax.php"`. Terms not found; no login on index.
- **caselaw:** **none found usable in these checks.** [Official judiciary](https://judiciary.gov.fj/) returned **403**; [PacLII Fiji](https://www.paclii.org/fj/) also failed. Judgment search/document routes and official terms/robots were not verified. PacLII qualifications above apply.

### fm — Federated States of Micronesia

- **legislation — official court-sponsored resource, copies explicitly unofficial:** [FSM Code](https://fsmlaw.org/fsm/code/index.htm). **VERIFIED—index.** English national code, state-law links and regulations. The page links a **2014 Code**, but its older HTML consolidation explicitly says it is updated only through **Public Law 12-12, August 2001**. Do not treat the old HTML as current. Static `.htm` chapter links; no API verified.
- **caselaw — official court-sponsored resource:** [FSM decisions](https://fsmlaw.org/fsm/decisions/index.htm). **VERIFIED—index.** Supreme Court and related jurisdictional material; English, static HTML links. Full coverage/count and current search operation not verified.
- **Shared restrictions:** [Disclaimer](https://fsmlaw.org/disclaimer.htm) says `"These documents are within the public domain"` but also `"intended for personal, not commercial, uses."` Flag **personal/non-commercial restriction**. [Robots](https://fsmlaw.org/robots.txt) returned **406 ModSecurity**; ordinary direct requests also encountered blocking. No login on web-opened indexes.

### ir — Iran

- **caselaw — official:** [Judiciary Research Institute judgment database](https://ara.jri.ac.ir/). **VERIFIED—text:** [judgment 41692](https://ara.jri.ac.ir/Judge/Text/41692). Homepage displayed **43,701 published judgments**, dated **1389/02/25–1405/05/31 in the Persian calendar**. Trial, appeal, administrative and Supreme Court material; Persian. HTML documents use `/Judge/Text/{id}`. Keyword, court and date filters exist; their request parameters/API remain unverified. [Robots](https://ara.jri.ac.ir/robots.txt): **404**. Footer: `"کلیه حقوق برای پژوهشگاه قوه قضاییه محفوظ است"`—all rights reserved. No separate automation restriction found; guest reading works.
- **legislation — official:** [National Laws and Regulations System](https://www.qavanin.ir/). **VERIFIED—index**, with title/text/date/issuer search. A linked `/Report/BookView/189` opened only a viewer shell: **full text UNVERIFIED**. Persian laws/regulations; coverage unknown. [Robots](https://www.qavanin.ir/robots.txt) returned an HTML transfer page, not usable directives. Terms not found. The alternative Majlis research site, `rc.majlis.ir`, timed out.

### ki — Kiribati

- **legislation:** **none found independently usable.** The official [Parliament legislation page](https://parliament.gov.ki/index.php/passage-of-legislation) directs readers to PacLII. [PacLII Kiribati](https://www.paclii.org/ki/) was inaccessible; a search-indexed [2019 Act PDF](https://www.paclii.org/ki/legis/num_act/kia2019209.pdf) was not verified by opening. English; scope/count unknown. No official API, document route or quotable terms verified.
- **caselaw — official candidate:** [Kiribati Judiciary](https://kiribatijudiciary.gov.ki/). Search results describe High Court, Court of Appeal and Magistrates’ Courts, but opening timed out: **UNVERIFIED** judgment availability. [Robots](https://kiribatijudiciary.gov.ki/robots.txt) opened with WordPress administrative exclusions, including `"Disallow: /wp-admin/"`. Terms and document routes unverified. PacLII remains a blocked fallback.

### kp — North Korea

- **legislation — other official government, not DPRK official:** South Korea’s [UNILAW](https://unilaw.go.kr/Index.do), a government unification-law resource. **VERIFIED—index.** Korean-language North Korean legal materials and related research; document currency, counts and text-versus-scan composition unverified. No working API or stable document pattern established. [Robots](https://unilaw.go.kr/robots.txt): **404**; reuse terms unverified.
- **caselaw:** **none found.** Checked UNILAW and searches for DPRK court judgments; no usable judgment corpus identified. No verified DPRK official or reputable LII alternative. Search results discussing trials are not judgment texts.

### kr — South Korea

- **legislation and caselaw — official:** [National Law Information Center](https://www.law.go.kr/) and [Open API service](https://open.law.go.kr/LSO/index.html). Korean statutes/regulations and judicial precedents; scope/count not revalidated. The public pages opened as application shells: **UNVERIFIED document access in this run**.
- **Machine access, retained from repository research:** `/DRF/lawSearch.do?OC={id}&target=law|prec|detc&type=JSON|XML&query=...`; documents through `/DRF/lawService.do` with target and document identifiers.
- **Requirement:** **free OC registration plus registered server IP/domain**; each self-hoster needs its own arrangement. No signup attempted. [Robots](https://www.law.go.kr/robots.txt): `"Allow: /"`. Full terms were not retrieved. **Not a zero-signup adapter candidate.**

### kw — Kuwait

- **legislation — official candidate:** [Government laws and regulations](https://e.gov.kw/sites/KGOenglish/Pages/Business/InfoSubPages/LawsAndRegulations.aspx). Search-indexed civil/commercial laws; **UNVERIFIED**, opening and [robots](https://e.gov.kw/robots.txt) returned **403**. Formats, API and terms unverified.
- **caselaw — official candidate:** [Ministry of State for National Assembly Affairs constitutional judgments](https://mona.gov.kw/constitcourt.aspx). Search index showed **11 selected constitutional judgments**, including 2009/2012 material, Arabic. **UNVERIFIED:** page and [robots](https://mona.gov.kw/robots.txt) returned **403**.
- **Result:** none found usable. [MoJ](https://www.moj.gov.kw/) was also checked; no working open full-text corpus established. Its robots endpoint returned 404.

### kz — Kazakhstan

- **legislation — official:** [Adilet example law](https://adilet.zan.kz/eng/docs/Z1900000293). Russian, Kazakh and selected English texts; routes `/rus/docs/{id}`, `/kaz/docs/{id}`, `/eng/docs/{id}`. Search engines expose text, but direct access returned a JavaScript shell: **UNVERIFIED live full-text retrieval**.
- [Robots](https://adilet.zan.kz/robots.txt) explicitly includes `"Disallow: /api/"`, `"Disallow: /search"` and `"Disallow: /advanced-search"` with general `"Allow: /"`. Comments welcome user-requested AI retrieval, but **search/API exclusions still apply**. Separate reuse terms not verified.
- **caselaw:** **none found usable.** Official [Judicial Office](https://office.sud.kz/) timed out. Constitutional Court searches surfaced announcements rather than a verified judgment collection. Document routes, terms and authentication requirements remain unverified.

### lk — Sri Lanka

- **legislation — official candidate:** [Government Printing Department, 2026 Acts](https://www.documents.gov.lk/view/act/acts_2026.html). Search index listed **15 Acts for 2026**, with Sinhala, Tamil and English versions. Department landing pages opened, but the annual Acts page timed out: **UNVERIFIED document access**. PDF delivery indicated; exact download pattern not established. [Robots](https://documents.gov.lk/robots.txt): **404**. Terms not found.
- **caselaw:** **none found usable in these checks.** [Supreme Court](https://supremecourt.lk/) and its [robots](https://supremecourt.lk/robots.txt) returned **403**. LawNet has a previously recorded TLS hostname problem; [CommonLII Sri Lanka](https://www.commonlii.org/lk/) failed with 403/410 depending on fetch method. Full-text search, terms and document routes unverified.

### mh — Marshall Islands

- **legislation — official:** [Nitijela legislation by title](https://rmiparliament.org/cms/legislation/acts-of-nitijela/by-title.html). **VERIFIED—index.** English Acts and amendments, including recent 2024–2025 entries; consolidated status varies. Joomla/iLAWS catalogue; document downloads and search request parameters not verified. [Robots](https://rmiparliament.org/robots.txt): **403**; terms not found.
- **caselaw — official:** [Marshall Islands Judiciary](https://rmicourts.org/), with [Supreme Court](https://rmicourts.org/supreme-court-decisions/recent-supreme-court-decisions/), [selected High Court](https://rmicourts.org/selected-high-court-decisions/) and [Traditional Rights Court](https://rmicourts.org/traditional-rights-court-decisions/) collections. **VERIFIED—site/navigation; individual full texts UNVERIFIED.** English and Marshallese; recent decisions indexed through 2026. HTML descriptions and linked PDFs; selected High Court material is described as scanned.
- [Robots](https://rmicourts.org/robots.txt) excludes administration/private plugin paths, including `"Disallow: /wp-admin/"`. [Disclaimer](https://rmicourts.org/disclaimer/): `"provided for general information only"`; footer `"All rights reserved."` No login encountered.

### my — Malaysia

**Existing blockers retained; no attempt made to undo encryption or evade prohibited routes.**

- **legislation — official:** [Laws of Malaysia](https://lom.agc.gov.my/). Federal legislation, Malay/English; PDF documents. Repository research found intentionally encrypted listing responses and protected links. **UNVERIFIED anew.** [Terms](https://lom.agc.gov.my/tnc.php) describe free access/download, but that does not resolve machine access. [Robots](https://lom.agc.gov.my/robots.txt) repeatedly returned **500** in the existing research; parent [AGC robots](https://www.agc.gov.my/robots.txt) disallows all.
- **caselaw — official:** [eJudgment](https://ejudgment.kehakiman.gov.my/EJudgmentWeb/SearchPage.aspx). Repository research verified JSON search via `eJudgmentService.asmx/GetEJudgmentPortalSearchList`; full documents use `efs.kehakiman.gov.my/EFSWeb/DocDownloader.aspx?DocumentID={guid}&Inline=true`. **UNVERIFIED anew.**
- **Explicit restrictions:** [EFS robots](https://efs.kehakiman.gov.my/robots.txt): `"Disallow: /efsweb/docdownloader.aspx"`. [Judiciary copyright](https://www.kehakiman.gov.my/en/copyright) requires `"express prior written consent of Chief Registrar's Office Federal Court of Malaysia"`.
- [CommonLII Malaysia](https://www.commonlii.org/my/) also failed. **No usable unrestricted alternative found.** Evidence retained in [research/my.md](../my.md).

### nr — Nauru

- **legislation and caselaw — official:** [RONLAW](https://ronlaw.gov.nr/), also identified by the [Nauru government](https://www.nauru.gov.nr/parliament-of-naoero/ronlaw-naoero%27s-online-legal-database.aspx).
- Search indexing shows Acts, regulations, gazettes and court decisions, including recent material; English. **UNVERIFIED full-text access:** opening produced an Angular application shell. API, search requests and document URLs not established.
- [Robots](https://ronlaw.gov.nr/robots.txt) returned the same HTML shell rather than directives. Terms not found; authentication requirements unverified. No challenge was identified, but a working shell does not prove working document retrieval.

### nz — New Zealand

- **legislation — official:** [NZ Legislation](https://www.legislation.govt.nz/); [API example](https://api.legislation.govt.nz/v0/works?search_term=privacy). English legislation. **UNVERIFIED anew:** repository research established an API-key requirement; website requests encounter **AWS WAF**, with robots returning HTTP 202/empty content. Key requested from the Parliamentary Counsel Office; no request made. [API terms](https://www.legislation.govt.nz/learn-more/legislation-data/api-terms-of-use/) not freshly retrieved.
- **caselaw — official:** [Courts of New Zealand Supreme Court judgments](https://www.courtsofnz.govt.nz/judgments/supreme-court). **VERIFIED—index.** Public-interest judgments page covers roughly the latest 90 days; linked English PDFs and [RSS](https://www.courtsofnz.govt.nz/judgments/supreme-court/RSS). Broader historical collection access was not established.
- **Restrictions:** [Copyright](https://www.courtsofnz.govt.nz/utilities/copyright): `"You can copy protected information for your personal or in-house use."` Other uses require consideration/permission. [Robots](https://www.courtsofnz.govt.nz/robots.txt) includes `"Disallow: /search/"` and a Supreme Court search-query exclusion. **Not an unrestricted general-purpose candidate.**

### om — Oman

- **legislation — official:** [Ministry of Justice and Legal Affairs laws](https://www.mjla.gov.om/laws/1). **VERIFIED—text:** [linked law PDF](https://www.mjla.gov.om/modules/laws/download.php?file=Book377528.pdf) downloaded successfully and yielded Arabic text, although extraction contained damaged characters. Laws/decrees include historical and current material; sampled PDF was a 1972 law. Catalogue pagination `/laws/1/page/{n}`; metadata `/laws/ar/1/show/{id}/`; PDFs `/modules/laws/download.php?file={filename}`. No API verified.
- **Policy:** footer states `"محتويات هذا الموقع مرخصة بموجب الرخصة الحكومية المفتوحة - سلطنة عٌمان"`—content licensed under the Oman Open Government Licence—and links the [government licence page](https://opendata.gov.om/ar/community/laws/3569a8ab-fc2b-41d7-8a80-f01f39e6fe8d). [Robots](https://www.mjla.gov.om/robots.txt) includes `"Disallow: /search"`; ordinary law routes were not excluded. Web-tool fetches sometimes timed out, while direct requests worked.
- **caselaw — official, limited:** [Supreme Judiciary Council collections](https://www.sjc.gov.om/InnerPage.aspx?ID=2095bd1d-1eca-4996-90e0-76652101f3c3&csrt=10038335971140681584&culture=en). **VERIFIED—index.** Criminal, civil, commercial and labour collections, approximately **2011–2025**, principally Arabic with selected English principles. PDF anthologies; many are **principles rather than complete individual judgments**. [Robots](https://www.sjc.gov.om/robots.txt): **404**. Footer `"Copyright © Supreme Judiciary Council"`; broader terms unverified.

### pg — Papua New Guinea

- **legislation — official candidate:** [Parliament Act PDF](https://www.parliament.gov.pg/uploads/acts/14A-22.pdf). Search-indexed English legislation; route `/uploads/acts/{filename}.pdf`. **UNVERIFIED by document opening**; current catalogue location, completeness, text layer, terms and robots were not established.
- **caselaw:** **none found usable.** The official [court library database page](https://www.pngjudiciary.gov.pg/court-library/library-database) points to PacLII. [PacLII PNG](https://www.paclii.org/pg/) was unavailable. Paid print/report services do not supply the requested free live corpus.

### pw — Palau

- **legislation — official candidate:** [Palau National Code](https://www.palaulaw.gov.pw/palau-national-code). Search index says updated through **RPPL 12-8, 21 July 2026**; English. **UNVERIFIED full text:** opening produced a JavaScript shell. [Robots](https://www.palaulaw.gov.pw/robots.txt) also returned the application shell. API, PDFs and terms not verified.
- **caselaw — official:** [Palau Judiciary decisions](https://palaucourts.gov.pw/upload-1.cshtml). Index opening timed out, but **VERIFIED—text:** [2026 Palau 3](https://palaucourts.gov.pw/doc/NeutralCitations/2026/2026%20Palau%203.pdf), a seven-page English appellate judgment. Documents follow `/doc/NeutralCitations/{year}/{citation}.pdf`; broader coverage/count unverified. [Robots](https://palaucourts.gov.pw/robots.txt): **404**. Terms not found; sample PDF required no login.

### qa — Qatar

- **legislation and caselaw — official:** [Al Meezan](https://almeezan.qa/). Arabic/English legislation and Court of Cassation rulings. **VERIFIED—application shell only; full-text API operations UNVERIFIED anew.**
- Repository research mapped `https://api.moj.gov.qa/api/v1`, including `/Legislation/search-index`, `/legislations/{id}`, `/Ruling/search-index` and `/rulings/{id}`. These are mapped routes, **not newly validated API calls**.
- **Explicit restriction:** the previously retrieved CMS `Terms_of_Use` says `"No content may be copied, reproduced, distributed, or used without prior written permission."` Exact quote and provenance are in [research/qa.md](../qa.md). [Robots](https://almeezan.qa/robots.txt): `"Allow: /"`; this does not override terms.
- **Alternative caselaw — official:** [QICDRC judgments](https://www.qicdrc.gov.qa/judgments). English court judgments, HTML/PDF. Prior [copyright terms](https://www.qicdrc.gov.qa/privacy-policy-data-protection) allow personal/in-firm use but require permission for public/commercial reuse. [Robots](https://www.qicdrc.gov.qa/robots.txt) previously specified `"Crawl-delay: 10"`. **Permission remains unresolved; no unrestricted alternative found.**

### sa — Saudi Arabia

- **legislation — official:** [Bureau of Experts laws](https://laws.boe.gov.sa/). Arabic consolidated legislation and selected English translations. **UNVERIFIED working access:** page and robots requests timed out.
- **caselaw and legislation — official:** [MoJ legal portal](https://laws.moj.gov.sa/). Judicial decisions and legislation; Arabic. **UNVERIFIED full text in this run**; portal timed out. Repository research maps backend prefix `https://laws-gateway.moj.gov.sa/apis/legislations/v1`; individual current operations were not verified.
- [MoJ portal robots](https://laws.moj.gov.sa/robots.txt): `"Allow: /"`. **Written approval is already recorded as required** under terms §4/linking provisions in [SIGNUPS.md](../SIGNUPS.md); exact current wording was not obtainable, so no invented quotation is supplied.
- Board of Grievances service searches did not establish an alternative anonymous full-text endpoint. **No immediately usable unrestricted source found.**

### sb — Solomon Islands

- **legislation — official:** [Attorney-General legislation](https://attorneygenerals.gov.sb/legislation/). **VERIFIED—index only.** English legislation; numerous displayed entries linked to `#` placeholders, so this is not yet a working corpus. A constitution download failed. [Robots](https://attorneygenerals.gov.sb/robots.txt): empty `"Disallow:"`. Terms not found.
- Alternative official [OAG constitution download](https://www.oag.gov.sb/resources/legislation/166-si-constitution-1978/file.html) was search-indexed but **UNVERIFIED by opening**.
- **caselaw:** **none found usable.** [PacLII Solomon Islands](https://www.paclii.org/sb/) was unavailable. Private Solomon Law Reports material examined was summaries/commentary, not a verified full-judgment substitute.

### sy — Syria

- **legislation:** **none found as a verified usable corpus.** [MoJ](https://moj.gov.sy/) opened as an official news/administrative site. Private [Syria Law legislation](https://www.syria.law/index.php/legislation/)—**other**, not official/LII—opened an index, but full statutes were not verified. Coverage, document patterns and reuse terms remain unknown.
- **caselaw:** **none found.** [Syria Law case-law page](https://www.syria.law/index.php/case-law/) contains English principles/summaries, not verified judgment texts; MoJ content did not establish a judgment database.
- Official [robots](https://moj.gov.sy/robots.txt) includes `"Disallow: /wp-admin/"`. No quotable official content-use terms found. No account-free full-document workflow established.

### th — Thailand

- **legislation — official candidates:** [Royal Gazette](https://ratchakitcha.soc.go.th/), Office of the Council of State sources already covered in repository research. Thai legislation, chiefly PDFs. Gazette and [robots](https://ratchakitcha.soc.go.th/robots.txt) returned **403**. Prior OCS checks found a JavaScript shell and certificate problems on a legacy host. **UNVERIFIED usable access.**
- **caselaw — official:** [Supreme Court Deka](https://deka.supremecourt.or.th/). Page and [robots](https://deka.supremecourt.or.th/robots.txt) timed out. Search/API/document patterns and terms not verified.
- **Result:** none found usable from official sources. Private [deka.in.th](https://deka.in.th/deka?type=judgment) is an **unverified other-source lead**, not an established nonprofit LII or cleared substitute.

### tl — Timor-Leste

- **legislation — official:** [Jornal da República](https://www.mj.gov.tl/jornal/). **VERIFIED—index.** Laws, decree-laws and other instruments from the independence period, with UNTAET material; Portuguese/Tetum. PDF pattern `/jornal/public/docs/{year}/serie_1/{filename}.pdf`; [2023 example](https://www.mj.gov.tl/jornal/public/docs/2023/serie_1/SERIE_I_NO_19_SUPLEMENTO_I.pdf) was search-indexed, not fully verified by opening.
- [Robots](https://www.mj.gov.tl/robots.txt): `"Crawl-delay: 10"` and `"Disallow: /search/"`, plus administrative paths. Terms not found; no login on index.
- **caselaw:** **none found usable.** Official [court search](https://www.tribunais.tl/busca.htm) says `"Sítio em manutenção!"`. The Gazette’s [Tribunal de Recurso category](https://www.mj.gov.tl/jornal/?q=node/6635) opened, but listed *deliberações* were not established to be full judicial judgments. Court terms/robots and document access remain unverified.

### to — Tonga

- **legislation — official:** [Attorney-General legislation by category](https://ago.gov.to/cms/legislation/index/index-by-category.html). **VERIFIED—index.** Revised legislation; English/Tongan. iLAWS catalogue; individual download format, consolidation dates and search parameters unverified.
- **caselaw — official:** [Attorney-General judgments](https://ago.gov.to/cms/judgements.html). **VERIFIED—index.** Some categories are empty; visible small collections include probate, admiralty and disciplinary material. Complete coverage and actual judgment downloads unverified.
- **Shared policies:** [Robots](https://ago.gov.to/robots.txt): **403**. [Publication policy](https://ago.gov.to/cms/ago-materials/publications/publication-policy.html) was located/opened, but a reliable operative reuse clause was not established. **No quoted permission or automation clearance claimed.** No login encountered on indexes.

### tv — Tuvalu

- **legislation — official:** [Tuvalu legislation by category](https://www.tuvalu-legislation.tv/cms/legislation/index/by-category.html?view=index_by_category). **VERIFIED—index.** English Acts/regulations, including pre-independence material and entries through **2025**. iLAWS catalogue; document download/text layer and search parameters unverified.
- Footer: `"All Legislation © 2026 The Tuvalu Government"`. [Robots](https://www.tuvalu-legislation.tv/robots.txt): **403**. Separate terms not found.
- **caselaw:** **none found usable.** [PacLII Tuvalu](https://www.paclii.org/tv/) returned access failures; no independent official judgment collection located.

### vu — Vanuatu

- **caselaw — official:** [Judiciary judgments](https://judiciary.gov.vu/court-activity/judgments). **VERIFIED—text:** [Peau v Jack](https://judiciary.gov.vu/court-activity/judgments/2912), 20 October 2026. Supreme Court/Court of Appeal judgments, index **2017–2026**, English. Full HTML plus PDF links; `/court-activity/judgments/{id}`. Search form exists; request parameters/API not verified.
- [Robots](https://judiciary.gov.vu/robots.txt) excludes administrative paths and `"Disallow: /api/"`; the verified judgment route is not excluded. No separate terms or automation ban found; no login/challenge encountered.
- **legislation — official, limited scope:** [Vanuatu Financial Services Commission legislation](https://www.vfsc.vu/legislation/). **VERIFIED—index.** Finance/company/business legislation, including **2026 consolidations**, English/French; linked PDFs. [Robots](https://www.vfsc.vu/robots.txt): empty `"Disallow:"`. Terms and PDF text layers unverified.
- The [Parliament consolidated-law page](https://parliament.gov.vu/index.php/parliamentary-business/acts-of-parliament/vanuatu-consolidated-legislation) points to PacLII’s **2006** consolidation; it is not an independent complete current source.

### ws — Samoa

- **legislation — official:** [Attorney-General consolidated laws](https://www.ag.gov.ws/consolidation-of-laws-of-samoa/). **VERIFIED—text:** [Attorney-General’s Office Act 2013](https://www.ag.gov.ws/wp-content/uploads/2024/02/Attorney-Generals-Office-Act-2013.pdf), a 12-page text PDF. **2023 consolidation**, English; alphabetical catalogue and `/wp-content/uploads/{year}/{month}/{filename}.pdf`. No API verified.
- [Robots](https://www.ag.gov.ws/robots.txt): **404**. Copyright footer present; separate reuse terms not found. No login/challenge on the sampled PDF.
- **caselaw:** **none found usable.** [PacLII Samoa](https://www.paclii.org/ws/) failed; no independent official full-judgment source established.

### ye — Yemen

- **legislation — court-branded source; official status not independently corroborated:** [Hadramout Court legislation](https://had-jc.com/legislation-laws). **VERIFIED—index.** Approximately **29 links** to constitution/laws, mainly **1990–2012**, Arabic. Linked PDFs; individual full texts and text layers unverified. [Robots](https://had-jc.com/robots.txt) includes `"Disallow: /wp-admin/"`. Terms not found.
- **caselaw:** **none found.** The above site and [MoJ](https://moj.gov.ye/) searches did not establish a usable full-judgment corpus; news and legal commentary do not qualify. Court coverage, document patterns and policy permissions remain unverified.

## Jurisdictions needing case law only

### af — Afghanistan — caselaw

**None found.** The official [Supreme Court](https://www.supremecourt.gov.af/) opened, but displayed news rather than a usable judgment collection; earlier research recorded an empty decisions section. Dari/Pashto site; judgment coverage/count unknown. **VERIFIED—site only, UNVERIFIED corpus.** [Robots](https://www.supremecourt.gov.af/robots.txt) has Drupal exclusions including `"Disallow: /search/"`. Terms, document routes/API and any access requirements unverified.

### au — Australia — caselaw

**Official:** [High Court judgments, 1998–current](https://www.hcourt.gov.au/cases-and-judgments/judgments/judgments-1998-current). **VERIFIED—text:** [O’Connell v DPP, [2026] HCA 41](https://www.hcourt.gov.au/cases-and-judgments/judgments/judgments-1998-current/oconnell-v-director-public-prosecutions) links a successfully opened **47-page text PDF**, plus DOCX.

The index displayed **1,679 results**, English, **1998–2026**. Keyword/case-number filters exist; exact request parameters not mapped. Documents use `/sites/default/files/eresources/{date}/HCA/{filename}.pdf`; HTML metadata uses judgment slugs.

Footer: `"Copyright 2025 Commonwealth of Australia"`. [Robots](https://www.hcourt.gov.au/robots.txt) timed out; an old copyright URL returned 404. **Full current reuse policy remains unverified.** No login on documents. Federal Court document and robots requests returned 403, making the High Court the better verified technical lead here.

### bt — Bhutan — caselaw

**Official:** [Judiciary judgment archive](https://www.judiciary.gov.bt/archive-content/judgments). **VERIFIED—text:** [Tashi Commercial Corporation judgment](https://www.judiciary.gov.bt/archives/1697605632-.pdf), five-page text PDF.

Small mixed archive: **11 rows**, approximately seven actual judgments, with other publications mixed in; English/Dzongkha. PDFs under `/archives/{filename}.pdf`; no verified API/search endpoint. [Robots](https://www.judiciary.gov.bt/robots.txt) timed out. Terms not found; sample required no login. **Useful but limited coverage, with robots unresolved.**

### hk — Hong Kong — caselaw

**Official:** [Judiciary judgments information](https://www.judiciary.hk/en/legal_ref/judgments.htm), [Legal Reference System](https://legalref.judiciary.hk/lrs/common/ju/judgment.jsp). English/Chinese judgments; prior research established frame-based HTML and document identifiers. **Full-text access UNVERIFIED anew.**

**Explicit restrictions:** [LRS robots](https://legalref.judiciary.hk/robots.txt): `"User-Agent: *"` / `"Disallow: /"`. Judiciary guidance says `"Judgments may be downloaded for private study and research only."` Commercial use requires application.

HKLII is an LII fallback, but previously identified API routes are robots-disallowed. **No unrestricted usable route established.**

### id — Indonesia — caselaw

**Official, constitutional jurisdiction only:** [Constitutional Court JDIH decisions](https://jdih.mkri.id/produk-hukum/putusan?frase=&page=1&search=&tahun=). **VERIFIED—index:** displayed **5,060 items**, with **2003–2026** years; Indonesian.

Search/list parameters visible in the URL: `frase`, `page`, `search`, `tahun`. PDF documents include [this indexed example](https://s.mkri.id/public/content/persidangan/putusan/putusan_mkri_5343.pdf), but its full text was not freshly opened. No JSON API verified.

[Robots](https://jdih.mkri.id/robots.txt): empty `"Disallow:"`. **Mixed access:** web opening worked, direct HTTP returned **403**. Terms not found; CDN robots unverified. Supreme Court’s broader `putusan3` source has a previously recorded Cloudflare block. **Promising, but not yet a reliably verified full-text adapter.**

### il — Israel — caselaw

**Other nonprofit academic source:** [Cardozo VERSA](https://versa.cardozo.yu.edu/), not the official Israeli courts and not a comprehensive LII.

**VERIFIED—site and opinion text.** Selected Israeli Supreme Court opinions translated into English; historical and recent material, current total unknown. HTML `/opinions/{slug}` and PDF attachments under `/sites/default/files/upload/opinions/`. No API verified.

[Robots](https://versa.cardozo.yu.edu/robots.txt): `"Crawl-delay: 10"` and `"Disallow: /search/"`, with Drupal administrative exclusions. [Terms page](https://versa.cardozo.yu.edu/terms-and-conditions) links onward to institutional terms; the operative reproduction licence was **not verified**. No login observed. Official Supreme Court document access remains affected by the connection failures recorded in repository research.

### iq — Iraq — caselaw

**Official candidate:** [Federal Supreme Court](https://www.iraqfsc.iq/), Arabic constitutional judgments. **UNVERIFIED working access:** homepage and [robots](https://www.iraqfsc.iq/robots.txt) returned **403**.

Higher Judicial Council/Iraq legal-database alternatives have previously recorded Cloudflare barriers. No working full-text search/API or reliable document pattern established. Terms and login requirements unverified. **None found usable.**

### jp — Japan — caselaw

**Official:** [Courts judgment search](https://www.courts.go.jp/hanrei/search2/index.html?lang=ja). **UNVERIFIED working corpus:** it redirected to maintenance, stating `"The system is currently undergoing maintenance."`

Japanese judgments, with historically indexed PDFs; complete coverage/count and current document routes not verified. [Robots](https://www.courts.go.jp/robots.txt) did not exclude the `hanrei` route in the retrieved rules. Terms not found; no current account requirement established. **Strong official lead, temporarily unverified rather than absent.**

### kh — Cambodia — caselaw

**Official candidates:** [Constitutional Council](https://www.ccc.gov.kh/index_en.php) and [Extraordinary Chambers in the Courts of Cambodia](https://www.eccc.gov.kh/).

The Council returned **HTTP 200 with `"Request Rejected"`**, including on [robots](https://www.ccc.gov.kh/robots.txt); that is not a working page. ECCC timed out. Search found an [ECCC-hosted 2001 Constitutional Council decision](https://www.eccc.gov.kh/sites/default/files/legal-documents/Const_Council_Res_on_KR_Law_12_Feb_2001.pdf), but it was **UNVERIFIED by opening**.

Khmer and selected English/French documents; no verified complete collection, search/API, terms or anonymous document workflow. **None found usable in these checks.**

### la — Laos — caselaw

**None found.** Official [People’s Supreme Court](https://peoplecourt.gov.la/) and its [robots](https://peoplecourt.gov.la/robots.txt) were unavailable/timed out. Searches did not establish a functioning official or reputable LII judgment collection.

All coverage, counts, document patterns, terms and authentication details remain **UNVERIFIED**. This is a search outcome, not a claim that no judgments are ever published.

### mv — Maldives — caselaw

**Official:** [Supreme Court judgment registry](https://www.supremecourt.mv/case-registry/judgments). **VERIFIED—index/metadata**, principally Dhivehi; full coverage/count unknown.

Actual judgment PDFs were not verified. Repository research records Cloudflare problems on the legacy document host. No current public API or stable functioning document pattern established. [Robots](https://www.supremecourt.mv/robots.txt) was permissive in prior research, **not freshly revalidated**; terms unverified. **None found with a complete working full-text workflow.**

## Jurisdictions needing legislation only

### cn — China — legislation

**Official:** [NPC National Laws and Regulations Database](https://flk.npc.gov.cn/). Chinese laws/regulations and associated legal instruments. Prior research mapped:

- POST `/law-search/search/list`
- GET `/law-search/search/flfgDetails?bbbs={id}`
- GET `/law-search/download/pc?bbbs={id}&format=docx`

These operations were **not re-exercised after checking the current policy**.

**Explicit automation ban:** [robots.txt](https://flk.npc.gov.cn/robots.txt) states:

> `#禁止使用任何自动化工具、脚本、爬虫程序采集或复制网站数据`  
> `User-agent: *`  
> `Disallow: /`

The comment prohibits automated tools/scripts/crawlers collecting or copying site data. **Reject for the proposed adapter without permission**, despite the absence of bulk crawling/training.

Alternative official [MoJ administrative-regulations database](https://xzfg.moj.gov.cn/) opened only an application shell; [robots](https://xzfg.moj.gov.cn/robots.txt) returned 404. Its full texts, API and terms remain **UNVERIFIED**. **No verified unrestricted substitute found.**

### jo — Jordan — legislation

**Official, useful limited alternative:** [Ministry of Justice laws](https://www.moj.gov.jo/EN/List/Laws). **VERIFIED—text:** [Law No. 10 of 2022 amending the Penal Code](https://www.moj.gov.jo/ebv4.0/root_storage/en/eb_list_page/law_no._10_of_2022_-_law_amending_the_penal_code.pdf), a ten-page English text PDF.

The English listing exposes at least ten selected laws/amendments from **2014–2023**; Arabic material also available. HTML list to `/ebv4.0/root_storage/en/eb_list_page/{filename}.pdf`; no API verified. **Not a complete consolidated national corpus.**

[Terms](https://www.moj.gov.jo/EN/Pages/Terms_of_Use) prohibit interference including `"overloading"` and `"flooding"`; no general automation ban found there. Footer: `"All Rights Reserved"`. Separate copyright policy could not be retrieved. [Robots](https://www.moj.gov.jo/robots.txt): **404**. Later requests encountered **451**, so reliability needs checking.

The official [Gazette issue 6038](https://www.pm.gov.jo/Ar/Pages/NewsPaperDetails/6038) also opened, but document links led to a DocuWare shell, **not verified PDF text**; [robots](https://www.pm.gov.jo/robots.txt): 404. The previously documented encrypted `lob.gov.jo` portal remains unresolved.

### kg — Kyrgyzstan — legislation

**Official:** [Ministry of Justice legal database](https://cbd.minjust.gov.kg/). Kyrgyz/Russian legislation; scope/count unverified.

**UNVERIFIED working text:** web opening produced a JavaScript shell; direct requests failed with **`TLSV1_ALERT_PROTOCOL_VERSION`**. Existing research also records connections dropped for the project client.

[Robots](https://cbd.minjust.gov.kg/robots.txt) previously allowed access, but could not be freshly verified because of transport failure. Terms, working search/API and document patterns unverified. **No usable alternative found.**

### mn — Mongolia — legislation

**Official:** [Legalinfo, National Legal Institute](https://legalinfo.mn/). **VERIFIED—text:** [Currency Regulation law](https://legalinfo.mn/mn/detail/15789), including an English translation labelled unofficial.

Mongolian laws/regulations and selected English translations; sampled law dates from **1994**, but overall coverage/count unknown. HTML document routes include `/mn/detail/{id}` and `/mn/detail?lawId=...`; English translation routes also occur. Search request parameters/API not verified.

[Robots](https://legalinfo.mn/robots.txt): **404**. Separate terms not found. Login widgets exist, but **the sampled document opened anonymously**. Earlier recorded unreachability was not reproduced. **Strong technical candidate, with reuse policy still unconfirmed.**

### np — Nepal — legislation

**Official:** [Nepal Law Commission alphabetical Acts index](https://www.lawcommission.gov.np/pages/alphabetical-index-of-acts/). **VERIFIED—index**, Nepali; historical and recent Acts, including entries through **2081 BS**. Category example: [constitutional bodies/governance](https://lawcommission.gov.np/category/1762/).

The current catalogue exposes category metadata, but **individual full-document links/text were not established**. The older [repository documents page](https://repository.lawcommission.gov.np/np/documents/) timed out. No API or reliable PDF pattern verified.

[Current-site robots](https://www.lawcommission.gov.np/robots.txt): `"User-agent: *"` / `"Crawl-delay: 10"`. Repository-host robots timed out. Terms not found; no login on current indexes. **Useful official lead, not yet a verified full-text adapter.**

### tw — Taiwan — legislation

**Official:** [Ministry of Justice Laws and Regulations Database](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=B0000001). **VERIFIED—text:** complete Civil Code HTML. Traditional Chinese; separate English translations exist, but were not tested here. Overall count/year range not established.

**Machine access:** `GET /LawClass/LawAll.aspx?pcode={code}` returns whole-law HTML. Search and single-article routes should **not** be used under the current robots rules. No permitted on-demand JSON/XML API verified.

[Robots](https://law.moj.gov.tw/robots.txt):

> `Disallow: /`  
> `Allow: /News/NewsDetail.aspx`  
> `Allow: /LawClass/LawAll.aspx`  
> `Allow: /SearchEngineSitemap.aspx`

[Copyright policy](https://law.moj.gov.tw/Service/Copyright.aspx) applies Taiwan’s Open Government Data Licence and states:

> `使用者亦無須取得本機關之書面或其他方式授權；然使用時應註明出處。`

Meaning: no separate written/other authorisation is needed, but attribution is required. **No login or challenge encountered. Best-cleared fetch-by-code candidate.**

## Ranked shortlist: next adapters

Ranking favours **official, anonymous, verified text**, with automation restrictions respected. “No ban found” is weaker than an affirmative licence; unresolved terms are shown explicitly.

| Rank | Jurisdiction / half | Source and proposed scope | Why it ranks here | Remaining limitation |
|---:|---|---|---|---|
| **1** | **tw / legislation** | [MOJ whole-law HTML](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=B0000001), fetch by known `pcode` | Verified text, no login, explicit robots allowance, open-government reuse terms | **Do not implement disallowed on-site search routes.** |
| **2** | **vu / caselaw** | [Vanuatu Judiciary](https://judiciary.gov.vu/court-activity/judgments) | Verified full HTML judgments; ordinary document routes not robots-excluded; no login/block observed | Separate reuse terms not found; search parameters still need mapping. |
| **3** | **ir / caselaw** | [Judiciary Research Institute](https://ara.jri.ac.ir/) | Verified HTML judgment; substantial published collection; anonymous access | Rights-reserved footer; no separate terms found; robots 404 and search mapping incomplete. |
| **4** | **mn / legislation** | [Legalinfo](https://legalinfo.mn/) | Verified HTML statutes; anonymous access now works | Reuse terms unconfirmed; robots 404; preserve translation-status labels. |
| **5** | **ws / legislation** | [Samoa AG consolidation](https://www.ag.gov.ws/consolidation-of-laws-of-samoa/) | Official indexed Acts and verified text PDF; no login | 2023 consolidation; terms not found; robots 404. |
| **6** | **bn / caselaw** | [Brunei Judiciary](https://www.judiciary.gov.bn/judgments/) | Working official index and verified text PDF | Copyright reserved; substantive terms not found; robots 404. |
| **7** | **pw / caselaw** | [Palau Judiciary](https://palaucourts.gov.pw/upload-1.cshtml) | Verified text judgment and predictable citation-based PDFs | Index timeout; terms unconfirmed; robots 404. |
| **8** | **om / legislation** | [Oman MJLA](https://www.mjla.gov.om/laws/1) | Official, anonymous downloads; site explicitly invokes an open-government licence | Sample PDF text has encoding damage; search robots-disallowed; licence details need review. |

**Next investigation, before adapter work:** Australia’s High Court has excellent verified text PDF/DOCX delivery, but its current robots and reuse policy remain unresolved. Jordan’s MoJ has verified text PDFs, but narrow coverage, an unretrieved copyright policy and an observed 451 response keep it below the shortlist.
