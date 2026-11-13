# Fontes — Round 2 source research: Europe and Americas

**Checked: 7 November 2026. Repository unchanged.**

The strongest new discoveries are Jamaica’s public legislation API, Chile’s Constitutional Court search API, and Liechtenstein’s separate Supreme Court archive. Each has qualifications described below.

**Verification convention:** **VERIFIED** means the specified page, response or document opened during this round—not that the entire source is suitable. **UNVERIFIED** means document retrieval or another stated requirement remains unconfirmed. Web-reader success is distinguished from direct HTTP success where they differed. Historical findings carried forward from the repository are identified explicitly.

Unless stated otherwise, corpus totals and complete date ranges were **not established**. Missing terms, a permissive robots file, and free access are not treated as affirmative reuse licences. No accounts were created, credentials used, or bot challenges bypassed.

## Case law

### `by` — Belarus — CASE LAW

**None found that could be verified as usable.**

- **Official candidates checked:** [Supreme Court](https://court.gov.by/) and [Constitutional Court](https://www.kc.gov.by/).
- **Access:** Both sites and their robots endpoints timed out in direct checks. No working search, individual judgment, document format, date range or count was verified.
- **Policies:** [Supreme Court robots](https://court.gov.by/robots.txt) and [Constitutional Court robots](https://www.kc.gov.by/robots.txt) were unreadable; terms could not be inspected. No policy quotation is available.
- **Status:** **UNVERIFIED.** Timeouts do not establish geo-blocking. Searches did not produce a verified, reputable alternative judgment corpus.

### `ee` — Estonia — CASE LAW

**1. Supreme Court English judgments — official, permission required**

- **Source:** [Supreme Court judgments](https://www.riigikohus.ee/en/judgments).
- **Coverage/access:** Selected English translations, particularly constitutional judgments; listings include 2026 decisions. HTML index links individual texts. This is not comprehensive Estonian-language case law.
- **Terms:** The page states: **“No reproduction, copy or transmission of these texts may be made without the prior permission in writing of the copyright holder.”**
- **Robots:** [robots.txt](https://www.riigikohus.ee/robots.txt) includes **“Disallow: /search/”**; document access is not generally excluded.
- **Status:** **VERIFIED** index and restriction. Not suitable for unrestricted reproduction.

**Other checked routes:** [RIKOS robots](https://rikos.rik.ee/robots.txt) freshly returned **“User-agent: *” / “Disallow: /”**. The repository also records Riigi Teataja’s exclusions for case-law routes. **None found with both suitable access and established permission.**

### `li` — Liechtenstein — CASE LAW

**1. Oberster Gerichtshof archive — official, working historical alternative**

- **Source:** [OGH decisions](https://www.ogh.li/entscheidungen-des-ogh). The current judiciary site identifies this as the archive for **2020–2025**. German; total uncounted. Older years appear in the selector but their contents were not verified.
- **Access:** HTML listing; individual PDFs under `/files/attachments/{filename}.pdf`. [Sample OGH 2025.74](https://www.ogh.li/files/attachments/17-va-2024-125-ogh-2025-74.pdf) opened as a **36-page text PDF**. No login.
- **Terms:** [Impressum](https://www.ogh.li/impressum): **“Eine kommerzielle Nutzung bedarf der vorhergehenden schriftlichen Genehmigung.”** Commercial use requires prior written permission. No explicit automation or AI/TDM clause was found.
- **Robots:** [robots.txt](https://www.ogh.li/robots.txt) returned **404**.
- **Status:** **VERIFIED** listing, document and terms. Useful for non-commercial historical access; not an unrestricted or current comprehensive source.

The central [Gerichtsentscheide robots](https://www.gerichtsentscheide.li/robots.txt) still says **“User-agent: *” / “Disallow: /”**.

### `lu` — Luxembourg — CASE LAW

**1. Judiciary open-data releases — official, licensed but wrong delivery granularity**

- **Source:** [Cour de Cassation dataset](https://data.public.lu/en/datasets/cour-de-cassation-1/).
- **Coverage:** French-language Cassation decisions; **48 downloadable resources**, not 48 judgments. Annual archives include 2021–2026; latest update displayed **2 November 2026**. Complete historical range not audited.
- **Access:** Annual ZIPs; the 2026 archive is 12.5 MB. No individual-judgment endpoint was established. Archives were not downloaded.
- **Licence:** Dataset expressly says **“Creative Commons Attribution - pas de modification (CC BY-ND)”**. Preserve attribution and account for the no-derivatives condition.
- **Robots:** [robots.txt](https://data.public.lu/robots.txt) returned **404**.
- **Status:** **VERIFIED** metadata/licence; archive contents **UNVERIFIED**. Not a good fit for live, one-judgment retrieval.

**2. Justice jurisprudence portal — official, restrictive**

- **Source:** [National jurisprudence](https://justice.public.lu/fr/jurisprudence.html); ordinary, administrative, social and Cassation decisions, plus JUDOC extracts.
- **Access:** HTML navigation and PDFs; a Cassation page redirected to a captcha.
- **Terms:** [Conditions générales](https://justice.public.lu/fr/support/aspects-legaux/conditions-generales.html): **“Les documents ne peuvent être utilisés qu'à titre personnel, pour information et dans un cadre strictement privé”**. Further clauses restrict redistribution and automated extraction of all or a substantial part without agreement.
- **Robots:** [robots.txt](https://justice.public.lu/robots.txt) includes **“Disallow: /*?*”**, with limited exceptions.
- **Status:** **VERIFIED** policies and landing page; unsuitable for unrestricted Fontes use. JUDOC extracts should not be represented as full judgments.

### `mt` — Malta — CASE LAW

**1. eCourts judgments — official, currently blocked**

- **Source:** [Judgment search](https://ecourts.gov.mt/onlineservices/Judgements/Search).
- **Coverage:** Government descriptions advertise selected judgments from **1944 onward**, in Maltese and English; corpus coverage was not independently verified.
- **Access:** Search returned an error; [robots.txt](https://ecourts.gov.mt/robots.txt) returned **403**. The repository records Cloudflare blocking and the PDF route `/onlineservices/Judgements/PrintPdf?CaseJudgementId={id}&JudgementId=0`; no document was retrieved this round.
- **Policies:** Terms and robots content could not be read; no quotation available. No successful public retrieval was established.
- **Status:** **UNVERIFIED** corpus/document access. **None found** that resolves the existing block without bypassing it.

### `ru` — Russia — CASE LAW

**1. СудАкт / Sudact — other, free unofficial aggregator**

- **Source:** [Sudact](https://sudact.ru/), [source description](https://sudact.ru/about/).
- **Coverage:** Supreme Court, arbitrazh, ordinary courts and magistrates; Russian. A 2026 judgment was verified; complete range and count remain unconfirmed.
- **Access:** Public HTML collections such as [`/vsrf/`](https://sudact.ru/vsrf/); documents follow `/{vsrf|arbitral|regular|magistrate}/doc/{id}/`. [Sample Supreme Court judgment](https://sudact.ru/vsrf/doc/QvaoO2KNOaT/) returned full HTML through both web and direct HTTP. Search-form parameters are exposed, but a complete query workflow was not validated.
- **Terms:** About page promises **“Бесплатный и надежный доступ для всех пользователей ко всем судебным актам.”** This establishes free access, not a reuse licence. The footer says **“Все права защищены”**. The linked [privacy policy](https://sudact.ru/politic/) concerns personal data; no affirmative content-reuse licence was found.
- **Robots:** [robots.txt](https://sudact.ru/robots.txt) excludes routes including **“Disallow: /vsrf/doc/print/”** and **“Disallow: /*/doc_ajax/”**; normal judgment HTML is not excluded.
- **Status:** **VERIFIED** document retrieval without login or captcha in the sample. Strong technical lead, **reuse permission unresolved**. Official Constitutional Court endpoints timed out.

### `cl` — Chile — CASE LAW

**1. Tribunal Constitucional search — official, working text API with incomplete document lookup**

- **Source:** [Constitutional Court search](https://buscador.tcchile.cl/).
- **Coverage:** Spanish constitutional judgments. Returned examples included cases from **2006 and 2020**; total corpus and full range unverified.
- **Access:** Public, unauthenticated JSON search:
  [`/api/extended/sentencias?filter={"search":"constitucion"}`](https://buscador-backend.tcchile.cl/api/extended/sentencias?filter=%7B%22search%22%3A%22constitucion%22%7D).
  It returned **95 matches for that query**, including judgment bodies. Text contains obvious OCR errors.
- **Document routes:** Frontend code exposes `/api/extended/sentenciaByID?filter=...` and `/api/extended/{id}/download`. Tested lookup identifiers returned empty results; the tested download returned 404. **These routes are not verified working.**
- **Policies:** No applicable reuse terms or AI/TDM clause was located. [Backend robots](https://buscador-backend.tcchile.cl/robots.txt) says **“User-agent: *” / “Disallow:”**. [Frontend robots](https://buscador.tcchile.cl/robots.txt) returned 404.
- **Status:** **VERIFIED** anonymous search and judgment text; individual-document retrieval and reuse permission remain unresolved.

The general judiciary’s `juris.pjud.cl` remains a repository-recorded robots exclusion; this Constitutional Court service is a separate source.

### `cr` — Costa Rica — CASE LAW

**1. Tribunal Supremo de Elecciones — official, useful but intermittently challenged**

- **Source:** [TSE jurisprudence](https://www.tse.go.cr/jurisprudencia.html), [search interface](https://www.tse.go.cr/juris/search.asp).
- **Coverage:** Spanish electoral and municipal jurisprudence. [Annual index](https://www.tse.go.cr/juris_anual.html) lists electoral years from **1946–2026**, with gaps, and municipal material from 1975. Count unknown.
- **Access:** HTML navigation/search, individual PDFs and annual ZIPs. [Decision 4190-E8-2025](https://www.tse.go.cr/imgs/info/4190-E8-2025.pdf) opened as **15 pages of extractable text**. Search submission was not validated.
- **Terms:** [Terms](https://www.tse.go.cr/terminos_condiciones_uso.html) state **“El acceso al sitio es gratuito”**; no express automation/AI prohibition was found in the retrieved text. The site footer links **CC BY-SA 4.0**; its application to every document was not independently established.
- **Robots:** [robots.txt](https://www.tse.go.cr/robots.txt) excludes paths such as **“Disallow: /private/”**, not jurisprudence.
- **Blocks/status:** **VERIFIED** pages and sample PDF through the web reader. Direct requests to terms/archive pages triggered **Radware captcha**. Not reliably accessible from the tested client.

Nexus remains excluded on the repository’s recorded parallel-database/robotic-access restriction.

### `cu` — Cuba — CASE LAW

**None found suitable.**

- **Checked source:** [Tribunal Supremo Popular](https://www.tsp.gob.cu/) — **official**.
- **Coverage/access:** Spanish bulletins, journals and institutional material; the homepage links a **2020–2021 bulletin**. No individual-judgment database was verified. Publication PDFs are not equivalent to searchable judgments.
- **Terms:** [Terms and conditions](https://www.tsp.gob.cu/terminos-y-condiciones) prohibit access **“utilizando medios automatizados, incluidos secuencias de comandos o rastreadores web”**.
- **Robots:** [robots.txt](https://www.tsp.gob.cu/robots.txt) includes **“Disallow: /search/”** and other Drupal exclusions. The separate contractual automation prohibition remains decisive.
- **Status:** **VERIFIED** homepage and prohibition. No automated adapter recommended.

### `gy` — Guyana — CASE LAW

**None found for a new domestic-court adapter.**

- **Supreme Court — official:** [Website](https://www.supremecourt.gy/) opened, but no usable public judgment corpus or document pattern was established. The eJudiciary login is not evidence that judgments are available anonymously. [robots.txt](https://www.supremecourt.gy/robots.txt) returned 404. No reuse terms were located; copyright footer present.
- **CommonLII — LII:** [Guyana section](https://www.commonlii.org/gy/) returned **403**. Its actual domestic-judgment holdings, years and formats remain **UNVERIFIED**. [Robots](https://www.commonlii.org/robots.txt) included **“Content-Signal: search=yes,ai-train=no,use=reference”**; this does not establish permission for an inaccessible collection. Terms could not be inspected.
- **CCJ:** Already covered by the repository’s `ccj` adapter. It is not a new replacement for Guyana’s domestic courts.

### `hn` — Honduras — CASE LAW

**1. IAIP Portal Único judiciary publications — official, promising index only**

- **Source:** [Judiciary resolutions on Portal Único](https://portalunico.iaip.gob.hn/384/26/).
- **Coverage:** Spanish constitutional, civil, criminal and labour resolutions, with listings through **2026**. Complete range/count unverified.
- **Access:** A substantial HTML publication table opened. The portal uses `/ver_archivo/{encoded-id}` downloads elsewhere, but an individual judgment download and its text quality were **not verified**. No verified search API.
- **Policies:** No applicable content-reuse terms were located. [robots.txt](https://portalunico.iaip.gob.hn/robots.txt) includes **“Content-Signal: search=yes,ai-train=no,use=reference”** and **“Allow: /”**, with administrative-path and named-bot exclusions.
- **Status:** **VERIFIED** listing; **UNVERIFIED** judgment retrieval. No login encountered on the listing.

The separate [judiciary jurisprudence portal](https://jurisprudencia.poderjudicial.gob.hn/) exposed an application shell; its robots request timed out. Do not count that as a working corpus.

### `ht` — Haiti — CASE LAW

**1. Cour de cassation — official, empty public collection**

- **Source:** [Judgment search](https://www.courdecassation.ht/consulter_arret/).
- **Access/coverage:** French search page opened and displayed **“Aucun arrêt trouvé.”** No document, date coverage or usable corpus verified.
- **Policies:** Footer says **“Tous droits réservés”**; no separate reuse terms found. [robots.txt](https://www.courdecassation.ht/robots.txt) returned 404.
- **Status:** **VERIFIED empty interface**, not a verified judgment source.

**2. Juricaf — university/judicial-association database, agent restriction**

- **Source:** [Juricaf](https://juricaf.org/). External references identify Haitian Cassation material, including a 2014 decision; holdings and document retrieval were not verified.
- **Robots:** [robots.txt](https://juricaf.org/robots.txt) explicitly lists **“ChatGPT-User”** and other OpenAI agents in a group with **“Disallow: /”**.
- **Status:** **UNVERIFIED** content; terms not inspected. No attempt was made to evade the agent restriction. **None found** meeting the requested conditions.

## Legislation

### `is` — Iceland — LEGISLATION

**1. Alþingi consolidated statute collection — official, text works in web reader but direct access blocked**

- **Source:** [Current law index](https://www.althingi.is/lagas/nuna/lagas.nofn.html).
- **Coverage:** Icelandic consolidated statutes; displayed edition **158a, 1 October 2026**. Total not reliably counted.
- **Access:** HTML index and full HTML statutes: `/lagas/{edition}/{year-number}.html`. [General Penal Code](https://www.althingi.is/lagas/158a/1940019.html) opened with substantial extractable text.
- **Reuse:** The [download explanation](https://www.althingi.is/lagasafn/zip-skra-af-lagasafni) explicitly contemplates **“lesa það inn í önnur kerfi eða samþætta öðrum vefjum”**—importing into other systems or integrating with websites. No separate comprehensive terms were located.
- **Robots:** [robots.txt](https://www.althingi.is/robots.txt) states **“Crawl-delay: 5”** and excludes search routes; statute paths are not excluded.
- **Status:** **VERIFIED** web-reader text; the same statute returned **403 to the direct Fontes HTTP client**. The bulk ZIP does not solve live per-document access.

### `lv` — Latvia — LEGISLATION

**1. Likumi.lv — official, written reuse agreement required**

- **Source:** [Likumi.lv](https://likumi.lv/); consolidated Latvian legislation.
- **Access:** Individual HTML acts use `/ta/id/{id}...`; current corpus count/range not audited this round.
- **Terms:** Publisher’s [reuse conditions](https://www.vestnesis.lv/atkalizmantosana) say **“Informācijas atkalizmantošana ar oficiālo izdevēju ir saskaņojama rakstveidā”**—reuse must be agreed with the publisher in writing.
- **Robots:** [robots.txt](https://likumi.lv/robots.txt) excludes **“/search.php*”** and additional version/document paths.
- **Status:** **VERIFIED** reuse requirement and robots. Not an unrestricted source.

**2. State Language Centre translations — official, limited alternative**

- **Source:** [Example translated regulation](https://www.vvc.gov.lv/en/laws-and-regulations-republic-latvia-english/cab-reg-no-291-certification-document-translations).
- **Coverage/access:** Selected English translations of Latvian legislation; sample metadata updated in 2024. Downloads use `/en/media/{id}/download?attachment=`; the sample returned **Microsoft Word**, whose text was not extracted.
- **Policies:** Footer: **“all rights of published content reserved.”** No affirmative reuse licence located. [Robots](https://www.vvc.gov.lv/robots.txt) excludes **“Disallow: /search/”**, not the sample media route.
- **Status:** **VERIFIED** metadata/download format; **UNVERIFIED** extraction and reuse suitability. Not comprehensive current consolidated law.

### `md` — Moldova — LEGISLATION

**1. Civil Aviation Authority legal-document mirror — official, narrow and dated**

- **Source:** [Civil Code PDF](https://www.caa.md/storage/upload/normative/normativ-reports/112/Codul%20civil_ro.pdf).
- **Coverage:** Romanian Civil Code, **870 pages**, consolidation shown through **20 July 2024**. This proves one substantial code, not comprehensive or current 2026 legislation.
- **Access:** Direct text PDF under `/storage/upload/normative/normativ-reports/{id}/{filename}`. No legislation search API established.
- **Policies:** No applicable reuse licence/terms located. [robots.txt](https://www.caa.md/robots.txt) has administrative/search exclusions, including **“Disallow: /search/”**; the PDF storage path is not excluded.
- **Status:** **VERIFIED** text PDF; useful only with explicit coverage/date limitations.

**Main source checked:** [Legis.md](https://www.legis.md/) and [robots.txt](https://www.legis.md/robots.txt) returned **403**. Its terms and current document access remain unverified.

### `me` — Montenegro — LEGISLATION

**None found with verified current text retrieval.**

**1. Government document library — official, unresolved lead**

- **Source:** [Labour Law document record](https://www.gov.me/dokumenta/d89fc734-bcd8-4283-a698-63608a60508c).
- **Coverage:** Search indexing identifies a Labour Law upload in 2025; that is not proof of its consolidation date. Montenegrin. Corpus scope/count unknown.
- **Access:** Observed record pattern `/dokumenta/{uuid}`; government downloads also use `https://wapi.gov.me/download/{uuid}?version=1.0`. The sampled record timed out; document text was not verified.
- **Policies:** [Government robots](https://www.gov.me/robots.txt), download-host robots and terms could not be read. No quotation available.
- **Status:** **UNVERIFIED**.

Also checked [Agency for Peaceful Resolution of Labour Disputes laws](https://amrrs.gov.me/zakoni/): page and robots timed out. The repository’s **image-only gazette** and **paid/restricted REGIS** findings remain unresolved.

### `rs` — Serbia — LEGISLATION

**1. National Assembly enacted laws — official, strong as-passed option**

- **Source:** [Enacted laws](https://www.parlament.gov.rs/akti/doneti-zakoni/doneti-zakoni.1033.html).
- **Coverage:** Serbian laws from the current parliamentary convocation, with **2024–2026** entries observed. Hundreds of listed items; exact count unverified. **As passed, not consolidated.**
- **Access:** HTML listing with PDF/DOC links; paths include `/upload/archive/files/lat/pdf/zakoni/14_saziv/{filename}.pdf`. [2026 amendment to the Judges Act](https://www.parlament.gov.rs/upload/archive/files/lat/pdf/zakoni/14_saziv/2445-26%20-%20Lat..pdf) opened as a text PDF. No login.
- **Policies:** No separate reuse terms or automation/AI prohibition located. Footer: **“© 2011 Narodna skupština Republike Srbije”**.
- **Robots:** [robots.txt](https://www.parlament.gov.rs/robots.txt) excludes certain `.txt` routes and other paths; the sampled public PDF route is not excluded.
- **Status:** **VERIFIED** listing and text document. Suitable technical next step, with reuse terms still unresolved.

The repository records an explicit automation ban for consolidated **PIS**; this parliamentary source is separate.

### `do` — Dominican Republic — LEGISLATION

**1. Consultoría Jurídica del Poder Ejecutivo — official, favourable content terms but unresolved search access**

- **Source:** [Legislation consultation](https://www.consultoria.gov.do/consultas?tab=legislacion).
- **Coverage:** Spanish laws, decrees, resolutions and gazettes; consolidation and full range/count unverified.
- **Access:** Repository-observed routes are `/api/consultas/search` and `/api/document/{DocId}`. The previous search request encountered Cloudflare; a successful document workflow was not established this round.
- **Terms:** [Terms](https://www.consultoria.gov.do/terminos) identify legal documents as **“documentos de dominio público”**. The prohibition concerns automated extraction **“que degraden el rendimiento de los servicios para la ciudadanía”**; it should not be reported as an unconditional ban on every automated request.
- **Robots:** [robots.txt](https://www.consultoria.gov.do/robots.txt) says **“Allow: /”**, excluding virtual-office, authentication and administration paths.
- **Status:** **VERIFIED** policies; **UNVERIFIED** working search/document pipeline. Public consultation is free; office certification services have separate registration.

**2. DGII Tax Code — official, restrictive reuse**

- **Source:** [Tax Code chapters](https://dgii.gov.do/legislacion/codigoTributario/Paginas/default.aspx).
- **Access:** Five chapter listings; [Title I](https://dgii.gov.do/legislacion/codigoTributario/Cdigo%20Tributario/Titulo1.pdf) verified as a **59-page text PDF**. Consolidation date not established.
- **Terms:** [Terms](https://dgii.gov.do/Paginas/TerminosUso.aspx): **“exclusivos para uso no comercial, sin derecho de venderlos o distribuirlos, ni de compilar o crear obras derivadas”**.
- **Robots:** [robots.txt](https://dgii.gov.do/robots.txt) excludes SharePoint infrastructure, including **“Disallow: /_layouts/”**, not these PDFs.
- **Status:** **VERIFIED**, but redistribution restriction makes it unsuitable without permission.

### `ec` — Ecuador — LEGISLATION

**1. National Assembly enacted laws — official, mixed-format as-passed source**

- **Source:** [Approved laws](https://www.asambleanacional.gob.ec/es/leyes-aprobadas).
- **Coverage:** Spanish enacted legislation; full range/count unverified. Not a consolidated-code service.
- **Access:** HTML listings and PDFs, including `/es/system/files/{filename}.pdf`. [2019 Ombudsman Law publication](https://www.asambleanacional.gob.ec/es/system/files/ro_ley_defensoria_del_pueblo.pdf) opened with extractable text. This corrects any blanket claim that **all** Assembly PDFs are scans; repository checks found scans among other samples.
- **Policies:** No applicable reuse terms/licence located. [robots.txt](https://www.asambleanacional.gob.ec/robots.txt) says **“Crawl-delay: 1”**, **“Disallow: /search/”**, and **“Disallow: /documents/”**. The verified `/es/system/files/` path is different.
- **Status:** **VERIFIED** one text-bearing law publication. Text quality needs checking per document.

**Rejected mirror:** The official [CNC laws page](https://www.competencias.gob.ec/caja-de-herramientas-2/gestionar-los-servicios-de-prevencion-proteccion-socorro-y-extincion-de-incendios/normativa/leyes/) links selected codes, but its sampled Labour Code was consolidated only through **2012** and included commercial Lexis editorial material. Government hosting does not establish permission for that material.

### `jm` — Jamaica — LEGISLATION

**1. Legal Information Portal Jamaica — official, strongest new legislation API; non-commercial restriction**

- **Source:** [LIPJ](https://lipj.gov.jm/), [advanced search](https://lipj.gov.jm/advanced-search).
- **Coverage:** English legislation. The official description lists revised-law editions, pre/post-1962 Acts, and gazette material from 1962 onward. Anonymous API pagination reported **17,963 records**—not necessarily distinct Acts.
- **Access:** **Verified public JSON**, no login/key:
  - Collection: [`/cms/api/records?pagination[pageSize]=1&populate[sourceFile]=true`](https://lipj.gov.jm/cms/api/records?pagination%5BpageSize%5D=1&populate%5BsourceFile%5D=true).
  - Individual text: [`/cms/api/records/82613?populate[ocr]=true&populate[document]=true`](https://lipj.gov.jm/cms/api/records/82613?populate%5Bocr%5D=true&populate%5Bdocument%5D=true).
  - The sample returned page-level OCR for a **2013 Toll Roads notice**, document metadata and a PDF reference. OCR has errors; the short title identifies the parent Act, not the notice’s full title.
- **Terms:** [Terms of Use](https://lipj.gov.jm/terms-of-use), retrieved through its [public CMS record](https://lipj.gov.jm/cms/api/pages/319?populate%5BportalComponents%5D%5Bpopulate%5D=*), say **“All official legal documents are public domain.”** However, services may be used **“only for lawful, non-commercial purposes”**. No explicit scraping or AI/TDM ban was found.
- **Robots:** [robots.txt](https://lipj.gov.jm/robots.txt) has an empty **“Disallow:”**.
- **Status:** **VERIFIED** anonymous record/text retrieval and terms. Strong candidate for qualifying non-commercial deployments; free software alone does not make every deployment non-commercial.

The older `laws.moj.gov.jm` still failed direct TLS validation; the replacement avoids that particular problem.

## Guatemala — both halves

### `gt` — CASE LAW

**1. Constitutional Court jurisprudence — official, partial working recovery**

- **Source:** [SJC jurisprudence](https://jurisprudencia.cc.gob.gt/sjc/).
- **Coverage:** Spanish constitutional judgments. Landing page exposes **36 landmark entries from 1991–2014**; this is not the size of the full database. A separate 2022 judgment was verified.
- **Access:** ASP.NET/DevExpress interface; successful search submission was not established. Direct documents use `/Sentencias/{stem}.pdf`. [Case 3670-2022](https://jurisprudencia.cc.gob.gt/Sentencias/850297.3670-2022.pdf) opened as a **20-page text PDF**.
- **Policies:** No affirmative reuse licence located. [robots.txt](https://jurisprudencia.cc.gob.gt/robots.txt) includes **“Content-Signal: search=yes,ai-train=no,use=reference”** and **“Allow: /”**, with named training-bot exclusions.
- **Status:** **VERIFIED** landing page and individual PDF. This does **not** prove the adapter’s previously failing search endpoint is fixed.

### `gt` — LEGISLATION

**1. CENADOJ penal-law compilation at USAC/CUNOC — university mirror of an official publication**

- **Source:** [Compilación de Leyes Penales de Guatemala, 2017](https://www.glifos.biblioteca.cunoc.edu.gt/library/images/2/2c/1141-Compilacion_de_Leyes_Penales-2017-1_Ed.-CENADOJ.pdf).
- **Coverage:** Spanish penal code and related laws, consolidated through **28 February 2017**; **432 pages**. Historical selection, not current comprehensive legislation.
- **Access:** Direct text PDF; no per-statute API/search. Verified through the web reader.
- **Terms:** Publication states **“Derechos reservados: © Organismo Judicial de Guatemala”**. No reuse licence located.
- **Robots:** The [robots request](https://www.glifos.biblioteca.cunoc.edu.gt/robots.txt) redirected to an OPAC HTML page; no usable robots policy was obtained.
- **Status:** **VERIFIED** historical text compilation; reuse and direct-client reliability unresolved. Not a current-law replacement.

Congress remains an unsuccessful route: its robots request returned **403**, consistent with the repository’s existing blocking findings. **None found for current comprehensive legislation with verified access and permission.**

## Ranked shortlist across jurisdictions

**No source received an unconditional “all requirements verified” rating.** These are the best next adapter targets, with the remaining conditions made explicit.

| Rank | Jurisdiction/source | Why pursue it | Remaining condition |
|---|---|---|---|
| **1** | **`jm` — LIPJ — OFFICIAL** | Anonymous JSON; 17,963 records; page-level text; public-domain legal documents; no express automation ban found | Portal use is non-commercial only; OCR and document metadata need care |
| **2** | **`rs` — National Assembly — OFFICIAL** | Working listing and text PDFs; free/no login; no relevant robots exclusion or automation ban found | As-passed laws only; affirmative reuse terms not located |
| **3** | **`cl` — Constitutional Court — OFFICIAL** | Working anonymous search API returns judgment text | Fix per-document lookup; OCR quality; reuse terms unresolved |
| **4** | **`ru` — Sudact — UNOFFICIAL** | Broad court categories; working full HTML; no login; ordinary document routes permitted by robots | Free-access statement is not a reuse licence; permission remains unresolved |
| **5** | **`ec` — National Assembly — OFFICIAL** | Verified text-bearing enacted-law PDFs; no login; permitted sampled path | Mixed scans/text, no consolidation, reuse terms unresolved |
| **6** | **`li` — OGH archive — OFFICIAL** | Working German text PDFs and historical index | Historical coverage; commercial use needs written permission |
| **7** | **`cr` — TSE — OFFICIAL** | Long electoral coverage, text PDFs, CC-linked footer | Radware challenges prevent reliable direct access; confirm licence scope |

**Existing-adapter repair priority:** `gt` case law—direct text PDFs work, but search still needs validation.

**Hold pending access resolution:** `is` Alþingi and `do` Consultoría. Both are more promising than replacing them with stale mirrors, but neither had a verified direct retrieval workflow this round.