**Fontes Africa source report — checked 6 November 2026**

I first read `research/SIGNUPS.md` and `research/mena_africa_international.md`, the matching regional research file. No repository files were changed, accounts created, or bot checks bypassed.

**Reading this report**

- **VERIFIED—text**: opened an actual document and saw readable text. **VERIFIED—index**: opened a working catalogue; document retrieval remains unverified. **UNVERIFIED**: search-only evidence, failed access, or an unusable application shell. All verification dates are **2026-11-06**, unless explicitly described as earlier repository evidence.
- Unless specified, **corpus count, complete year coverage, public JSON/XML API, and machine-search parameters were not established**. A visible search form does not establish an API.
- **Terms not located** means no substantive usage terms were found; it does **not** establish permission. Copyright notices are reported separately from explicit reproduction prohibitions.
- No login was required for the pages or documents actually verified. Authentication requirements for inaccessible resources remain unknown.
- Reported TLS, DNS and HTTP failures are observations from this check—not proof of geo-blocking or persistent downtime. No geo-block was established.

**Shared restriction affecting many African LIIs**

The Peachjam sites listed below have valuable collections, but their robots files now include:

> `Content-Signal: ai-train=no, search=yes, ai-input=no`  
> `Disallow: /api/`  
> `Disallow: /search/`  
> `Disallow: /judgments/`

They also disallow jurisdiction-specific judgment paths and specify `Crawl-delay: 5`. Some named search agents receive different directives, but those are not general permission for Fontes.

I call this **restriction P** below. It matters even without crawling or training: an MCP feeding retrieved text into a model should not assume `ai-input=no` is irrelevant.

The repository documents the historical Peachjam search route `/search/api/documents/?search=TEXT&doc_type=judgment&page=N`, returning JSON with HTML result fragments, and `/akn/...` document identifiers. **These are historical implementation leads, not newly verified or unrestricted APIs.** Earlier repository testing also recorded Cloudflare challenges on numerous document routes and an AWS challenge at Kenya Law.

---

**ao — Angola**

- **caselaw — official:** [Tribunal Constitucional, acórdãos](https://www.tribunalconstitucional.ao/pt/jurisprudencia/acordaos/). **VERIFIED—text:** [Acórdão 1161/2026](https://www.tribunalconstitucional.ao/pt/acordaos/ac%C3%B3rd%C3%A3o-n-%C2%BA-1161-2026/) contains the judgment in HTML. Portuguese constitutional and political-party litigation; 2026 decisions verified, total and earliest year unknown. Search fields include case/year/text; documents use `/pt/acordaos/{slug}/`, with some PDF alternatives. Terms not located; [robots](https://www.tribunalconstitucional.ao/robots.txt) returned 404. No challenge observed.
- **legislation — official:** [Diário da República](https://www.diariodarepublica.gov.ao/). **UNVERIFIED:** indexed material advertises free Série I access, with other services subscription-based, but the site failed with TLS/server-name errors. Document format, coverage and access conditions need verification. [Robots](https://www.diariodarepublica.gov.ao/robots.txt) likewise unavailable. The Constitutional Court also has a limited legislation section, but a general working legislative collection was not verified.

**bf — Burkina Faso**

- **legislation — official:** [LegiBurkina](https://legiburkina.gov.bf/accueil), including the indexed [regulatory-text catalogue](https://legiburkina.gov.bf/textesReglementaires). **UNVERIFIED—documents:** application shell opened, but usable results/document retrieval were not established. French laws and regulations; 2026 items appear in search indexing. API and document patterns unknown. [Robots](https://legiburkina.gov.bf/robots.txt): `User-agent: *` / `Disallow:`. Terms not located.
- **caselaw — official:** [Conseil constitutionnel](https://www.conseil-constitutionnel.gov.bf/). **UNVERIFIED:** indexed constitutional decisions and PDFs from 2024–2026, but direct access timed out/refused connections. Indexed PDFs use `/fileadmin/user_upload/…pdf`. Terms and [robots](https://www.conseil-constitutionnel.gov.bf/robots.txt) unavailable. Also checked the official gazette lead, [JOBF](https://jobf.gov.bf/); no better judgment source established.

**bi — Burundi**

- **legislation — official:** [Primature, lois promulguées](https://primature.gov.bi/category/lois-promulguees/). **VERIFIED—index:** French laws, codes and decrees, with instruments dated 2006–2026 visible. WordPress category pagination and document posts/download links; PDF text versus scans not tested. [Robots](https://primature.gov.bi/robots.txt): `User-agent: *` / `Disallow:`. Terms not located; no challenge observed.
- **caselaw — official:** [Cour constitutionnelle](https://courconstitutionnelle.gov.bi/). **VERIFIED—site/index**, individual judgments unverified. Its navigation groups decisions by the constitutions of 1992, 1998, 2001, 2005 and 2018; these are categories, not verified coverage bounds. French. [Robots](https://courconstitutionnelle.gov.bi/robots.txt): `Disallow: /wp-admin/`, with the usual admin-AJAX exception. Terms not located.
- Broader official alternative [Amategeko/CEDJ](https://amategeko.gov.bi/) remains **UNVERIFIED**: timeout and HTTP 503 on robots. Search-advertised collection counts were not independently confirmed.

**bw — Botswana**

- **legislation — official, externally hosted:** [Attorney General’s Chambers e-Laws](https://e-laws.botswanalaws.com/). **VERIFIED—text:** [Constitution](https://e-laws.botswanalaws.com/constitution-of-botswana/constitution-of-botswana/) is full HTML. English consolidated principal/subsidiary legislation, repealed acts and historical legislation; the site advertises historical material from 1890, but completeness was not audited. Category/slug URLs and a search field; no public API verified.
  
  [Usage policy](https://e-laws.botswanalaws.com/privacy-policy/) prohibits, among other things, “Disrupt website operations” and asserts government ownership. No explicit automation prohibition was found. [Robots](https://e-laws.botswanalaws.com/robots.txt) contains `Allow: /blog-news/*` and no `Disallow` directive. No login or challenge observed.
- **caselaw — official lead:** [Administration of Justice](https://www.justice.gov.bw/). **UNVERIFIED—documents:** access timed out. The [government’s access guide](https://gov.bw/law-crime-and-justice/access-laws-botswana?page=1) describes historical e-Laws judgments through 2012 and directs newer judgments to the judiciary. [Robots](https://www.justice.gov.bw/robots.txt): `Crawl-delay: 10`, `Disallow: /search/`. No functioning current judgment collection verified.

**cd — Democratic Republic of the Congo**

- **legislation — official:** [Journal officiel](https://journalofficiel.cd/). **UNVERIFIED—documents:** JavaScript shell opened without usable texts. [Robots](https://journalofficiel.cd/robots.txt) explicitly disallows `/journals`, `/publications`, `/recherche` and `/api/`; account/cart routes are also present. Terms and any payment requirement for documents remain unverified.
- **caselaw — official lead:** [Cour constitutionnelle](https://cour-constitutionnelle.cd/). **UNVERIFIED:** page timed out; [robots](https://cour-constitutionnelle.cd/robots.txt) was accessible and restricts `/wp-admin/`. No document retrieval verified.
- **Other fallback:** [Leganet](https://www.leganet.cd/) has indexed HTML legislation and gazette PDFs, but access failed with a self-signed-certificate error, including [robots](https://www.leganet.cd/robots.txt). **UNVERIFIED**, not a currently usable fallback.

**cf — Central African Republic**

- **legislation — none found as a verified usable collection.** Checked the official [embassy’s legal-text page](https://paris.diplomatie.gouv.cf/textes-officiels): **VERIFIED—index**, but its constitutional download was labelled a **draft**, not an enacted constitution. It should not be ingested as current law.
- **caselaw — other, judicial-association publication:** [AAHJF, *La Voix internationale de la justice*, issues 11–12](https://aahjf.net/images/Publications/montage_A5_2.pdf). **VERIFIED—text PDF**, 510 pages, containing selected regional constitutional jurisprudence including CAR material. French; CAR-specific count/date coverage not established. One bound PDF, no per-case search/API. [Robots](https://aahjf.net/robots.txt) restricts administrative directories, including `Disallow: /administrator/`; terms not located. This is a limited publication fallback, not a national judgment database.

**cg — Republic of the Congo**

- **legislation — official:** [Secrétariat général du gouvernement](https://sgg.cg/en/accueil.html). **VERIFIED—text PDF:** [Gazette 45/2026](https://sgg.cg/JO/2026/congo-jo-2026-45.pdf), 40 pages. French laws/decrees and gazettes; historical material is indexed, but complete coverage/count unknown. Pattern `/JO/YYYY/congo-jo-YYYY-NN.pdf`; catalogue/search interface.
  
  **Reproduction restriction:** [legal notice](https://sgg.cg/fr/mentions-legales.html) prohibits full or partial reproduction without “autorisation préalable et expresse”. [Robots](https://sgg.cg/robots.txt) has `User-agent: *` without a disallow. Do not shortlist without resolving the express reproduction restriction.
- **caselaw — official lead:** [Cour constitutionnelle](https://www.cour-constitutionnelle.cg/). **UNVERIFIED:** expired-certificate failure. Advertised document counts and coverage were not verified. Also found [Supreme Court judgments/opinions](https://coursupreme.cg/arrets-avis.html), but did not establish working document access.

**dj — Djibouti**

- **legislation — official:** [Journal officiel électronique](https://www.journalofficiel.dj/). **VERIFIED—text:** a [2026 arrêté](https://www.journalofficiel.dj/texte-juridique/arrete-n2026-103-pr-mass-portant-approbation-et-rendant-executoire-le-budget-previsionnel-de-lexercice-2026-de-lagence-djiboutienne-de-developpement-social-adds/) contains complete French HTML text. Laws, decrees, arrêtés and gazette issues; earliest year/count unknown. Document pattern `/texte-juridique/{slug}/`; keyword/date search forms, API unverified. Issue landing pages can render without their substantive contents, so individual-text routes are preferable.
  
  Footer: “Tous droits réservés”; legal-notice labels did not expose substantive terms. [Robots](https://www.journalofficiel.dj/robots.txt) restricts `/wp-admin/` and an internal plugin file, not public text routes. No login/challenge observed.
- **caselaw — official:** [Conseil constitutionnel decisions](https://www.conseil-constitutionnel.dj/decisions/). **VERIFIED—index:** constitutional/electoral decisions in French; full-document format, date range and count unverified. [Robots](https://www.conseil-constitutionnel.dj/robots.txt): `Crawl-Delay: 20`. Terms not located.

**er — Eritrea**

- **caselaw — none found.** Searches for an official court reporter or free judgment collection did not establish one. Legal research guides describe difficulty obtaining judgments; that is not proof that no judgments exist online.
- **legislation — other, intergovernmental fallback:** [FAOLEX Eritrea](https://faolex.apps.fao.org/countries/ERI). **UNVERIFIED—documents:** country interface opened, but individual texts were not tested. Indexed proclamations and sectoral legislation, including environmental/water legislation; English and original-language availability varies. No verified corpus count/API/document pattern.
- Another specific lead is the [Penal Code PDF hosted by UNODC](https://www.unodc.org/cld/uploads/res/document/penal-code_html/PENAL_CODE_ERITREA.pdf), **UNVERIFIED** in this check. These are limited international repositories, not Eritrean official publishing services. Source-specific reuse conditions remain unresolved.

**ga — Gabon**

- **legislation — official:** [Journal officiel](https://journal-officiel.ga/). **VERIFIED—site/text listings:** French laws, regulations and codes, including an indexed [2024 constitutional law](https://www.journal-officiel.ga/21489-002-r-2024-/). Numeric-title HTML slugs; no API verified. Public text is accessible alongside subscription offerings for the gazette; no login needed for the inspected pages. [Robots](https://journal-officiel.ga/robots.txt) was empty. Legal-notice link was nonfunctional; terms unresolved.
- **caselaw — none found as a verified judgment collection.** Checked constitutional-court leads, the gazette and the [ACCF court directory](https://accf-francophonie.org/cour/gabon/). A gazette page containing the Constitutional Court’s internal regulations is **legislation, not a judgment**.

**gh — Ghana**

- **legislation — official:** [Parliament, Acts](https://www.parliament.gh/docs?OT=&P=0&type=Acts). **VERIFIED—index:** English acts, including historical legislation from 1961 onward. Query includes `type=Acts` and pagination `P`; individual download format and completeness unverified. The web reader opened the catalogue, while direct requests encountered DNS resolution failures. Terms and [robots](https://www.parliament.gh/robots.txt) could not be established.
- **caselaw — official lead:** [Judicial Service eJudgment](https://ejudgment.judicial.gov.gh/). **UNVERIFIED:** timeout/DNS failure; court coverage, document routes and authentication unresolved.
- **LII fallback:** [GhaLII](https://ghalii.org/), Ghanaian judgments and legislation in English. **Restriction P verified** in [robots](https://ghalii.org/robots.txt); unrestricted live document access was not verified.

**gm — The Gambia**

- **legislation — official:** [National Assembly Acts](https://assembly.gm/documents/type/acts). **VERIFIED—index:** English act downloads, including historical and recent entries; total/year bounds unknown. HTML listing with PDF links; text-versus-scan quality untested. [Robots](https://assembly.gm/robots.txt): `User-agent: *` / `Disallow:`. Terms not located.
- **caselaw — other, nonprofit legal-information project:** [Law Hub Gambia law reports](https://satang-nabaneh.squarespace.com/gambia-law-reports). **VERIFIED—index:** selected Gambian judgments and law-report material, English; completeness/count/year span unverified. Static topic/report pages and downloads, no API verified.
  
  [Terms](https://satang-nabaneh.squarespace.com/terms-of-use): “not the copyright owner of statutes and case law” and “not able to give permission for reproduction”. No express automated-access ban found. [Robots](https://satang-nabaneh.squarespace.com/robots.txt) restricts `/search`, `/api/` and format-query routes. Public report pages opened without login.

**gn — Guinea**

- **caselaw and legislation — official:** [Cour suprême](https://coursupreme.org.gn/fr/). **VERIFIED—site/index:** national jurisprudence, court bulletins and codes/legislation are linked; French. Individual documents, complete year ranges and counts were not verified.
- **Client-specific prohibition:** [robots](https://coursupreme.org.gn/robots.txt) allows the generic agent but explicitly gives several named AI agents and download clients `Disallow: /`, including ChatGPT-User and GPTBot. Further document retrieval was not pursued after seeing this. Terms not located; not an unrestricted Fontes candidate.

**gq — Equatorial Guinea**

- **legislation — official:** [Boletín Oficial del Estado search](https://boe.gob.gq/buscador). **VERIFIED—search interface**, not document retrieval. Spanish gazette material; filters include title/content, category, dates and issue number. Coverage/count, request parameters and PDF quality unverified.
- [Robots](https://boe.gob.gq/robots.txt) includes `Disallow: /search/`; the opened interface is `/buscador`. Terms not located. No challenge observed on the interface.
- **caselaw — none found.** Checked national judiciary/constitutional-court and gazette search leads. Results about Spanish colonial legislation or Spanish court judgments were not treated as Equatoguinean case law.

**gw — Guinea-Bissau**

- **legislation — official:** [Assembleia Nacional Popular legislation](https://www.parlamento.gw/leis/legislacao). **VERIFIED—text:** [Constitution](https://www.parlamento.gw/leis/constituicao/constituicao-da-republica) is full HTML. Portuguese; a limited legislation collection, not verified comprehensive consolidated laws. Plone page/file URLs; no API/search query verified.
- [Robots](https://www.parlamento.gw/robots.txt): `User-agent: *` / `Disallow:`; Google-specific form exclusions also exist. Terms not located; no login/challenge observed.
- **caselaw — none found.** Checked Supreme Court, legal-guide and bar-association leads; no working public collection established.

**ke — Kenya**

- **caselaw and legislation — official:** [Kenya Law](https://kenyalaw.org/). Broad English-language court/tribunal judgments and consolidated legislation. **VERIFIED—policy; unrestricted document retrieval UNVERIFIED.** Corpus totals and complete dates were not re-established.
- **Explicit automation prohibition:** [terms](https://kenyalaw.org/terms-of-use/) state: “Scraping, deployment of unauthorized bots and bulk downloading from this website is strictly prohibited.” They describe permission/licensing requirements for automated access; no permission or API key was requested.
- [Robots](https://kenyalaw.org/robots.txt) also has **restriction P**. Historical `/akn/…` HTML/PDF routes and search JSON are documented in the repository, alongside AWS challenge failures. **Not a no-signup/no-permission adapter candidate.**

**km — Comoros**

- **legislation — official:** [Ministry of Justice legal texts](https://justice.gouv.km/legislation-et-textes-officiels/). **VERIFIED—interface**, document retrieval unverified. French laws/codes/decrees; search indexing exposes PDFs under `/wp-content/uploads/YYYY/MM/…pdf`, including a 2004 constitutional-court organic law. Catalogue counts and PDF text quality unknown.
- [Robots](https://justice.gouv.km/robots.txt) restricts `/wp-admin/` and an internal plugin file. Terms not located; no login observed.
- **caselaw — none verified.** A “jurisprudence” filter is not evidence of a populated collection. Checked the ministry and AHJUCAF historical-judgment leads; no working per-case collection established.

**lr — Liberia**

- **caselaw — official:** [Judiciary opinions](https://judiciary.gov.lr/opinions/), including [2026 Supreme Court decisions](https://judiciary.gov.lr/2026-supreme-court-of-liberia-decision/). **VERIFIED—index:** English Supreme Court opinions, local annual collections from 2016–2026. Older 1861–2015 links lead to LiberLII; those historical texts were not verified. Annual HTML lists with document links; no API verified.
- **legislation — official, limited:** [Judiciary Law](https://judiciary.gov.lr/judiciary-law/). **VERIFIED—text**, English HTML. The judiciary also links constitutional material; no comprehensive current statute collection verified.
- [Robots](https://judiciary.gov.lr/robots.txt): `Disallow: /wp-admin/`. Substantive reuse terms not located. No challenge/login observed.

**ls — Lesotho**

- **caselaw and legislation — LII:** [LesothoLII](https://lesotholii.org/). Best broad free collection identified: appellate/high-court judgments and legislation, principally English. Complete dates/counts not verified.
- **VERIFIED—robots; documents UNVERIFIED for unrestricted use.** [Robots](https://lesotholii.org/robots.txt) has **restriction P**. Historical Peachjam HTML/PDF and search routes apply as implementation leads only. No better working official collection was established; permission-free automation should not be assumed.

**ml — Mali**

- **legislation — official:** [SGG Journal officiel](https://sgg-mali.ml/fr/journal-officiel/le-journal-officiel.html). **VERIFIED—index:** the site displayed 2,419 gazette records across 67 years; these are site-reported figures, not an audited corpus. French; recent 2026 issues and historical issues visible. PDF pattern `/JO/YYYY/mali-jo-YYYY-NN.pdf`, including special issues.
- **Reproduction restriction:** [legal notice](https://sgg-mali.ml/fr/mentions-legales.html) prohibits reproduction without “autorisation préalable et expresse”. [Robots](https://sgg-mali.ml/robots.txt) gives no generic disallow. Working access does not resolve the reproduction restriction.
- **caselaw — official:** [Cour suprême jurisprudence](https://coursupreme.ml/jurisprudence/). **VERIFIED—index:** selected French decisions/compendia, including 2007–2008 and 2017–2023 material; newer links include Juricaf. Local PDFs and external links; no API verified. Footer: “Tous droits réservés”. [Robots](https://coursupreme.ml/robots.txt) has an empty `Disallow`. Individual PDF quality untested.

**mr — Mauritania**

- **legislation — official, limited:** [Primature laws](https://primature.gov.mr/t_lois). **VERIFIED—index:** a small list, approximately six entries, including constitutional material and 2012/2021 laws. Arabic titles and linked documents; full-text/scanned status unverified. Drupal node routes; no API verified. [Robots](https://primature.gov.mr/robots.txt) restricts search and administrative routes. Terms not located.
- **caselaw — official:** [Conseil constitutionnel, normative decisions](https://conseil-constitutionnel.mr/fr/?cat=17). **VERIFIED—index:** constitutional review and separate electoral categories; French/Arabic site. WordPress `?cat=` and `?p=` routes; full judgment content, counts and years unverified. [Robots](https://conseil-constitutionnel.mr/robots.txt) was empty. Terms not located.
- Bar-association gazette fallback [ONAM](https://www.onamauritanie.mr/?q=journal) failed TLS hostname validation.

**mw — Malawi**

- **caselaw and legislation — LII:** [MalawiLII](https://malawilii.org/). Broad English-language judicial and legislative collection; precise court/year coverage and counts not freshly verified.
- **VERIFIED—robots; unrestricted documents UNVERIFIED.** [Robots](https://malawilii.org/robots.txt) has **restriction P**. Historical Peachjam HTML/PDF/search routes are known, but no unrestricted public API was established. Official judiciary/parliament searches did not yield a better verified collection in this check.

**na — Namibia**

- **legislation — other, nonprofit:** [Legal Assistance Centre statutes](https://www.lac.org.na/index.php/laws/statutes/). **VERIFIED—index:** extensive English act/regulation listing, including pre-independence instruments and current legislation; [NAMLEX](https://www.lac.org.na/index.php/laws/namlex/) provides an accompanying index. Linked PDFs; individual text quality not tested. No public API/search protocol verified.
- Footer: “All Rights Reserved.” [Robots](https://www.lac.org.na/robots.txt) has an empty `Disallow`. Substantive reuse terms not located. Direct requests worked although the web reader timed out.
- **caselaw — official lead:** [eJustice High Court register/reports](https://www.ejustice.jud.na/High%20Court/RegisterAndReports/Pages/RegisterAndReports.aspx). **UNVERIFIED:** TLS issuer-chain failure/timeouts. SharePoint-style document library, with 2025 decisions indexed by search.
- **LII fallback:** [NamibLII](https://namiblii.org/); [robots](https://namiblii.org/robots.txt) has **restriction P**.

**ne — Niger**

- **legislation — official lead:** [Cour de cassation, 2020 legislative compilation](https://www.courdecassation.ne/images/lois/pdfs/Recueil_thematique_des_lois_et_reglements_Edition%202020.pdf). **UNVERIFIED:** indexed French PDF, but the host failed TLS hostname validation. Scope/count and PDF quality unverified; terms/robots unavailable.
- **caselaw — none found as a trustworthy working source.** The former domain `cour-constitutionnelle-niger.org`, still referenced by historical official links, now returned unrelated retail content. **Verified unsuitable**, not a current court source. Historical indexed judgment URLs on that domain should not be trusted without an independent archive.

**sd — Sudan**

- **legislation — official:** [Ministry of Justice publication files](https://moj.gov.sd/files/index/28). **VERIFIED—index:** Arabic official-gazette issues, including 2021 and 2025–2026 entries. HTML list linking files; actual PDF text/scans and complete coverage unverified. [Robots](https://moj.gov.sd/robots.txt) returned 404. Terms not located.
- **caselaw — official lead:** [Sudan Judiciary](https://sj.gov.sd/). **UNVERIFIED—documents:** judicial-report pages timed out; search indexing identifies historical report volumes. [Robots](https://sj.gov.sd/robots.txt) includes `Content-Signal: search=yes,ai-train=no,use=reference` and named-agent restrictions. Do not equate this with the Peachjam `ai-input=no` policy. Terms, document routes and current coverage unresolved.

**sl — Sierra Leone**

- **caselaw — official:** [Judiciary judgment listing](https://www.judiciary.gov.sl/?mo=2&page_id=76&yr=2027). **VERIFIED—index:** English Supreme Court, Court of Appeal and High Court judgment links, including 2022 material. The `yr=2027` parameter belongs to page/calendar state and **does not establish 2027 judgments**. PDF links; text quality/count unverified. [Robots](https://www.judiciary.gov.sl/robots.txt) returned 404; terms not located.
- **legislation — official lead:** [Parliament’s 2024 Acts](https://parliament.gov.sl/acts-2024-41.html). **UNVERIFIED—live access:** search-indexed list of enacted laws, but opening returned 502; the `www` host also failed certificate validation. PDF links generally use `/uploads/acts/…pdf`. Some similarly named files are bills and must not be treated as enacted acts. Terms/[robots](https://www.parliament.gov.sl/robots.txt) unavailable.
- **LII fallback:** [SierraLII legislation](https://sierralii.gov.sl/legislation/); [robots](https://sierralii.gov.sl/robots.txt) has **restriction P**.

**so — Somalia**

- **legislation — LII, institutional status not independently established:** [SomLII](https://somlii.org/). **VERIFIED—index:** 31 listed laws/constitutions, with Somali/English interface and entries spanning historical 1970s laws through documents labelled 2026. Coverage includes federal and member-state instruments. Individual documents and legal currency were not verified; do not infer current validity from titles alone.
- [Robots](https://somlii.org/robots.txt): `User-agent: *` / `Allow: /`. The site says linked source PDFs are the controlling reference and that repository copies are not authenticated. No explicit automation ban located. Cloudflare script present, but no blocking challenge encountered.
- **caselaw — none verified.** Official [judiciary](https://judiciary.gov.so/) failed DNS/access checks. No accessible national judgment corpus established.

**ss — South Sudan**

- **legislation — official lead:** [Ministry of Justice laws](https://mojca.gov.ss/laws/). **UNVERIFIED:** expired-certificate failure. Search indexing shows English acts, principally 2005–2017, and a [2011 Transitional Constitution PDF](https://www.mojca.gov.ss/wp-content/uploads/2023/03/Transitional-Constitution-of-the-Republic-of-South-Sudan-2011.pdf). WordPress upload routes; actual PDF quality, counts, terms and robots unverified.
- **caselaw — none found as a usable public collection.** Checked judiciary/legal-research leads and references to historical judgment compilations. Sudanese judgments were not counted as South Sudanese coverage.

**st — São Tomé and Príncipe**

- **caselaw — official:** [Tribunal Constitucional documents](https://tribunalconstitucional.st/documentos.php). **VERIFIED—index:** Portuguese constitutional/electoral decisions, including multiple 2026 judgments. Local `/docs/…pdf` and external Google Drive links; query form present, API unverified. Individual PDF text quality unknown. [Robots](https://tribunalconstitucional.st/robots.txt) returned 404; copyright footer, no substantive terms located.
- **legislation — official parliamentary collection hosted by Brazil’s Chamber:** [Constitutional legislation](https://www2.camara.leg.br/saotomeeprincipe/saotomeeprincipe/legislacao/legislacao-constitucional). **VERIFIED—index:** four constitutional instruments dated 1982, 1987, 1990 and 2003; adjacent electoral/parliamentary collections. Portuguese, HTML/file pages. [Robots](https://www2.camara.leg.br/robots.txt) restricts form/search routes, including `Disallow: /*search_form$`; no blanket ban on this collection. Reuse terms and individual download quality unresolved.

**sz — Eswatini**

- **legislation — official, limited:** [Judiciary legislation](https://www.judiciary.org.sz/legislation). **VERIFIED—index:** selected court/legal statutes, English; full extent and file quality unverified.
- [Robots](https://www.judiciary.org.sz/robots.txt) says “Public content is open to crawlers” but also disallows `/uploads/`, `/storage/` and `/search`. Document locations must be checked against those exclusions. Terms not located.
- **caselaw and broader legislation — LII/judiciary-supported:** [EswatiniLII](https://eswatinilii.org/). **Restriction P verified** in [robots](https://eswatinilii.org/robots.txt); unrestricted document retrieval not verified. Not an unrestricted fallback.

**td — Chad**

- **legislation — other, nonprofit CEFOD database:** [LegiTchad laws](https://legitchad.org/textes/lois/). **VERIFIED—index:** French laws, ordinances, decrees and arrêtés. Site counters showed 797 laws, 506 ordinances, 2,755 decrees and 615 arrêtés; these are displayed counts, not audited totals. Category lists and document links; API/search parameters and full-document format unverified.
- Footer: “Tous droits réservés”; substantive terms not located. [Robots](https://legitchad.org/robots.txt) returned 404. No login/challenge observed.
- Official alternatives [SGG gazette](https://jo.sgg.gouv.td/) and [Journal officiel](https://journalofficiel.td/fr) were respectively affected by TLS mismatch and an unproductive application shell.
- **caselaw — none verified.** Checked constitutional-council, court-association and gazette leads; no accessible judgment collection established.

**tg — Togo**

- **caselaw — official:** [Cour constitutionnelle decisions](https://courconstitutionnelle.tg/download-category/decisions/). **VERIFIED—index:** French constitutional/electoral decisions, including 2024–2026, with PDF downloads.
- **Explicit robots exclusion:** [robots](https://courconstitutionnelle.tg/robots.txt) gives the generic agent `Disallow: /`, with a separate Googlebot allowance. Do not treat that exception as permission for Fontes. Terms not located.
- **legislation — official lead:** [Journal officiel](https://www.jo.gouv.tg/). **UNVERIFIED—documents:** HTTP 526 encountered. Search indexing exposes historical/current gazette PDFs under `/sites/default/files/…pdf`; coverage and text quality not audited. [Robots](https://www.jo.gouv.tg/robots.txt): `Crawl-delay: 10`, `Disallow: /search/`, plus specific node exclusions. Terms unresolved.

**tn — Tunisia**

- **legislation — other, nonprofit DCAF:** [Security-sector legislation database](https://legislation-securite.tn/). **VERIFIED—site/index:** Arabic/French laws, codes and regulations; site advertises over 3,000 instruments from 1956 onward. This is a sectoral collection, not a verified complete national statute corpus. Individual HTML routes include `/latest-laws/{slug}/`; no public API verified.
- [Robots](https://legislation-securite.tn/robots.txt): `Crawl-delay: 10`, `Disallow: /search`, `Disallow: /wp-content/uploads/`. HTML and PDF routes therefore require different treatment. [Privacy policy](https://legislation-securite.tn/privacy-policy/) was accessible; no affirmative reuse licence established.
- Official [IORT](https://www.iort.gov.tn/) and prior `legislation.tn` leads did not yield a verified usable collection.
- **caselaw — official lead:** [Ministry of Justice jurisprudence](http://jurisprudence.e-justice.tn/). **UNVERIFIED:** timeout; terms, robots, documents and authentication unknown. No usable alternative verified.

**tz — Tanzania**

- **caselaw and legislation — official:** [Office of the Solicitor General e-Library](https://elibrary.osg.go.tz/). **VERIFIED—index:** separate judgments, legislation and gazette collections. English legislation metadata, including 1963 instruments, was visible; complete dates/counts and actual PDF quality unverified. DSpace `/items/{UUID}` and `/communities/{UUID}/…` routes; embedded page data exposed `/server/api/core/items/{UUID}` and bitstream endpoints, but public API responses were not tested.
- [Robots](https://elibrary.osg.go.tz/robots.txt): `Disallow: /search`, with administrative/workflow restrictions. Public items are labelled “Open Access”; login exists but was unnecessary for the catalogue. External subscribed databases listed in the footer are separate. Footer reserves rights; substantive reuse terms not located.
- **Alternative official caselaw source, restricted:** [Judiciary eMaktaba](https://emaktaba.judiciary.go.tz/) displayed 9,106 judgments. [Terms](https://emaktaba.judiciary.go.tz/privacy-policy?tab=terms-of-use) prohibit: “Perform automated scraping, bulk downloading, or data extraction without authorization.” This is an express blocker for an unapproved adapter. [Robots](https://emaktaba.judiciary.go.tz/robots.txt) returned 404.
- [TanzLII](https://tanzlii.org/) has **restriction P** in [robots](https://tanzlii.org/robots.txt).

**ug — Uganda**

- **caselaw and legislation — judiciary-supported LII:** [ULII](https://ulii.org/en/). English judgments and legislation; dates/counts not freshly verified. **VERIFIED—robots**, not unrestricted document access.
- [Robots](https://ulii.org/robots.txt) has **restriction P**. Historical Peachjam HTML/PDF and JSON search routes are not an unrestricted API.
- **Official legislation alternative:** [Parliament Acts](https://www.parliament.go.ug/acts). **UNVERIFIED:** TLS issuer-chain failure/timeouts; documents, terms and robots unresolved. No better verified unrestricted collection established.

**za — South Africa**

- **caselaw — official:** [Constitutional Court](https://www.concourt.org.za/), with the [official repository record](https://collections.concourt.org.za/items/163891f7-3660-4a96-8252-c43d57c8d67e). **VERIFIED—text PDF:** [*Mofokeng*, [2026] ZACC 43](https://collections.concourt.org.za/bitstreams/77cfb38f-3f26-49f5-b8d4-35eca5fb0e44/download), 36 pages. English Constitutional Court judgments; total/earliest date not established. DSpace `/items/{UUID}` and `/bitstreams/{UUID}/download`; distinguish judgments from separate media summaries.
- [Repository robots](https://collections.concourt.org.za/robots.txt) disallows `/search` and discovery/faceted routes, but not ordinary item/bitstream URLs. Named downloader bans also exist. Substantive reuse terms not located. No login/challenge observed.
- **legislation — official:** [Government Acts](https://www.gov.za/documents/acts). **VERIFIED—index:** national acts, including 2026 entries, HTML metadata and linked PDFs. [Robots](https://www.gov.za/robots.txt) restricts `/search/`. [Terms](https://www.gov.za/terms-and-conditions-use) permit copying/distribution “only for non-commercial informational or reference purposes”; commercial use requires approval. A free project should not assume every self-hosted deployment qualifies.
- SAFLII remains a reputable LII fallback, but earlier repository checks recorded challenges; it was not promoted over the working official Constitutional Court source.

**zm — Zambia**

- **caselaw — official:** [Judiciary Supreme Court decisions](https://judiciaryzambia.com/category/resources/decisions/supreme-court-decisions/). **VERIFIED—index and document landing page:** Supreme, Constitutional, Appeal, High and subordinate-court categories; English, recent 2025–2026 cases visible. Slug pages link `/wp-content/uploads/YYYY/MM/…pdf`.
- **Important reproduction restriction:** the [Caleb Mulenga decision page](https://judiciaryzambia.com/scz-07-08-2026-caleb-mulenga-vs-kansanshi-mining-plc-aug-2026-justice-mutuna/) states that no part may be “altered, edited, reproduced, adapted, or otherwise modified” without prior written permission. [Robots](https://judiciaryzambia.com/robots.txt) says `Allow: /`, but that does not cancel the document notice. **Not an unrestricted shortlist candidate.**
- **legislation — official lead:** [Parliament Acts](https://www.parliament.gov.zm/acts/volume/354). **UNVERIFIED:** TLS issuer-chain failure/timeouts. Indexed acts/PDFs exist; completeness and PDF quality unverified. Terms/robots unresolved.
- [ZambiaLII](https://zambialii.org/) has **restriction P** in [robots](https://zambialii.org/robots.txt).

**zw — Zimbabwe**

- **legislation — official:** [Parliament Acts](https://www.parlzim.gov.zw/acts/). **VERIFIED—index:** English act PDFs, including recent upload listings; complete dates/count and text-versus-scan quality unverified. HTML listing and linked files; no API verified. [Robots](https://www.parlzim.gov.zw/robots.txt) has a generic empty `Disallow` alongside a `/parlzim/` exclusion; the inspected `/acts/` route is different. Terms not located.
- **caselaw — LII:** [ZimLII](https://zimlii.org/). Best broad free collection identified; English judgments. **Restriction P verified** in [robots](https://zimlii.org/robots.txt); unrestricted document access not verified.
- Official Judicial Service Commission leads did not produce a verified replacement judgment collection in this check.

**et — Ethiopia — caselaw only**

- **Other, private free legal publisher:** [AbyssiniaLaw cassation decisions](https://abyssinialaw.com/decisions/federal-supreme-court-cassation-decisions?layout=table&start=0). **VERIFIED—index:** Federal Supreme Court cassation volumes 1–28, principally Amharic; recent volumes are labelled 2024–2026. Volume downloads rather than a verified per-case API. PDF text/scans not tested.
- [Robots](https://abyssinialaw.com/robots.txt) restricts `/uploads/`, `/media/`, `/components/`, login and registration routes. The listing works, but individual download paths require checking before automation. Terms not located; no login required for the listing.
- Official Federal Supreme Court failures were already documented in the repository. The [Federal Justice and Law Institute catalogue](https://fjli.gov.et/Tedocs/) opened but contained placeholder links/details; its advertised counts were **not treated as a real accessible corpus**.

**ly — Libya — caselaw only**

- **Official:** [Supreme Court, alolya.gov.ly](https://alolya.gov.ly/). **VERIFIED—site and judgment metadata:** [constitutional appeal 12/70](https://alolya.gov.ly/article/4b695a55-3fb9-44b6-bc68-51b8b2348081?from=/) has an accessible Arabic article page dated October 2026.
- **Full judgment text remains UNVERIFIED.** The page did not expose a readable judgment body or ordinary PDF link in the inspected response. Do not treat metadata/legal-principle posts as full judgments.
- Routes `/article/{UUID}`; [robots](https://alolya.gov.ly/robots.txt) says `Allow: /` but disallows `/api/`, `/pdf-viewer` and `/favorite`. Footer: “جميع الحقوق محفوظة” (“all rights reserved”). No substantive terms or public API verified. This working official host is a better lead than the previously blocked legacy domain, but not yet a verified full-text adapter.

**eg — Egypt — legislation only**

- **Other, independent legal archive:** [Manshurat](https://manshurat.org/). **VERIFIED—text:** [2025 Labour Law](https://manshurat.org/content/qnwn-lml-ljdyd-2025) is extensive Arabic HTML. Laws, codes, constitutional and regulatory material; complete dates/count unknown. `/content/{slug}` documents; no public API verified.
- [Robots](https://manshurat.org/robots.txt): `Crawl-delay: 10`, `Disallow: /search/`, plus internal routes. Public `/content/` pages opened without login or payment. Substantive reuse terms not located.
- **Correction to older research:** the inspected legislation is freely readable; this source should not be dismissed categorically as paid-only. Its independent status and unresolved reuse terms still distinguish it from an official open-data service.

**ng — Nigeria — legislation only**

- **Other, nonprofit:** [Policy and Legal Advocacy Centre, Laws of Nigeria](https://placng.org/lawsofnigeria/index.php?page=1). **VERIFIED—text:** [Acts Authentication Act](https://placng.org/lawsofnigeria/view2.php?sn=14) is readable English HTML.
- The collection is based on the **2004 Laws of the Federation**; do not present it as fully current or inclusive of subsequent amendments. Count not verified. Pagination `index.php?page=N`, documents `view2.php?sn=N`; keyword form present, exact submission parameters/API unverified.
- Footer: “Copyright Policy and Legal Advocacy Centre”. [Robots](https://placng.org/robots.txt) returned 404; substantive reuse terms not located. No login/challenge observed. No comparable comprehensive working official collection was verified.

---

**Ranked next-adapter shortlist**

These are **implementation prospects**, ranked by verified text access and fit. “No ban found” is narrower than an affirmative reuse licence.

| Rank | Source / half | Why it ranks here | Remaining limitation |
|---|---|---|---|
| **1** | **Botswana e-Laws — legislation** | Official; full HTML verified; no login; substantive usage policy checked; no explicit automated-access ban found. | Government copyright retained; test representative acts and the search request before implementation. |
| **2** | **Angola Constitutional Court — caselaw** | Official; complete judgment HTML verified; no login or challenge. | Terms not located; robots 404; court-specific coverage. |
| **3** | **Djibouti eJO — legislation** | Official; complete individual instrument in HTML verified; public text routes not excluded by robots. | Terms links unproductive; search parameters and historical coverage unverified. |
| **4** | **South Africa Constitutional Court — caselaw** | Official; full text-bearing judgment PDF verified; no login; direct item/document routes available. | Repository search routes excluded; reuse terms unresolved; Constitutional Court only. |
| **5** | **Liberia Judiciary — legislation, then caselaw** | Official HTML Judiciary Law verified; working current Supreme Court opinion listings. | Legislation is narrow; verify individual judgment files and reuse terms. |
| **6** | **Guinea-Bissau Parliament — legislation** | Official; Constitution HTML verified; permissive generic robots; no login. | Small collection; broader statute coverage and reuse terms unresolved. |
| **7** | **Egypt Manshurat — legislation** | Large readable Arabic law pages; no login/payment observed. | Independent source; search route excluded; reuse terms unresolved. |
| **8** | **Nigeria PLAC — legislation** | Nonprofit; simple, stable-looking HTML retrieval; no login. | Historical 2004 baseline; updates and reuse terms unresolved. |

**Next verification queue:** Tanzania OSG, Namibia LAC, Gambia Assembly, Burundi Primature and Zimbabwe Parliament have working catalogues, but individual document quality and terms need checking before they join the text-verified shortlist.

**Do not prioritize as unrestricted adapters:** Kenya Law; Peachjam sources with restriction P; Tanzania eMaktaba; Togo Constitutional Court; Guinea’s named-agent-restricted court site; Congo/Mali gazettes with express reproduction restrictions; and Zambia judiciary decisions carrying a prior-permission reproduction notice.
