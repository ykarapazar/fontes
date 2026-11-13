# Americas — open legal data sources (case law + legislation)

Researched 2026-11-05. Probes were made from a UK residential IP with a Chrome User-Agent, read-only GET/simple search, a handful per source.
"verified 2026-11-05" = I got real data back. "unverified" = docs/third-party claim only. **Geo-blocking matters:** several LatAm government
sites refused or timed out from a non-local IP. They may work from an in-country IP, but an MCP running on a user's laptop abroad will hit the same wall.

Tiers: **A** = official API, no key · **B** = official API, free key · **C** = HTML only, automated access allowed/tolerated · **D** = paid / forbidden / nothing usable.
`A*` = open API with no key, but **not official** (academic/NGO mirror) or undocumented internal API.

## Summary table

| Jurisdiction | Case law tier | Legislation tier | Best endpoint(s) | Auth | Notes |
|---|---|---|---|---|---|
| US federal | **B** (govinfo USCOURTS, CourtListener) | **A** (eCFR, Federal Register, uscode.house.gov HTML) / **B** (govinfo, Congress.gov) | `api.govinfo.gov/search` (POST, full-text federal opinions); `www.ecfr.gov/api/*`; `uscode.house.gov/us/usc/t{N}/s{S}/` | api.data.gov key (DEMO_KEY works for testing); CourtListener token | **CourtListener v4 search now returns 401 without a token**, and the free tier is 5/min, 50/h, **125/day**. govinfo is the better official full-text fallback for federal courts. |
| US states | B (CourtListener covers state appellate courts) / CAP static (historic) | B (Open States v3, LegiScan); state codes are mostly per-state HTML (C) | `v3.openstates.org` (bills, not codified law) | key | No single source for consolidated state codes. That needs about 50 HTML scrapers. |
| US historic (CAP) | A (static files, bulk-shaped) | – | `static.case.law/{reporter}/{vol}/cases/{page}-{n}.json` | none | CC0 since 2024. Static JSON per case, **no search API**. Frozen at 2018 or earlier. |
| Canada federal | **A\*** (A2AJ API) / B (CanLII, metadata only) | **A** (Justice Laws XML) | `api.a2aj.ca/search`, `/fetch`; `laws-lois.justice.gc.ca/eng/XML/{id}.xml` | none (A2AJ, Justice Laws) | A2AJ = free full-text API + hosted MCP over 31 courts/tribunals + all 13 provinces' statutes/regs (weekly mirror). |
| Canada provinces | A\* (A2AJ: BCCA, BCSC, ONCA, NSCA, NLCA, YKCA…) | A (BC Laws CiviX); A\* (A2AJ all provinces); C (Ontario e-Laws, LegisQuébec) | `bclaws.gov.bc.ca/civix/search/complete/fullsearch` | none | CanLII website sits behind a JS bot wall. CanLII API needs a key by request and returns **metadata only**. |
| Mexico | **D** (from abroad) / B? | C/D | `sjf2.scjn.gob.mx/services/sjftesismicroservice/api/public/tesis` (internal) | none, but Incapsula WAF | Every SCJN host (sjf2, bj, bicentenario) sat behind an Incapsula/JS challenge. diputados.gob.mx timed out from the UK. DOF homepage was reachable. |
| Brazil | **A\*** (STF internal search API) / D (DataJud, DJEN geo-blocked) | A (Senado dados abertos, slow) / C (LexML URN resolver) / D (Planalto blocked abroad) | `POST jurisprudencia.stf.jus.br/api/search/search` | none | STF ES-style API worked without a key. Planalto returned "Acesso Negado". LexML SRU hit a Senado WAF challenge. Rich MCP ecosystem already exists. |
| Argentina | A\* (SAIJ JSON search, flaky) | A\* (SAIJ) / C (argentina.gob.ar/normativa) | `www.saij.gob.ar/busqueda?r=…&o=&p=&f=…&v=colapsada` | none | SAIJ returns JSON but stems oddly and some field queries return 0. Infoleg `texact.htm` URLs redirect to "archivo inexistente". |
| Chile | C (juris.pjud.cl HTML; JSON behind CSRF, unverified) | **A** (BCN Ley Chile XML + JSON search) | `www.leychile.cl/Consulta/obtxml?opt=7&idNorma=…`; `nuevo.leychile.cl/servicios/Consulta/listaresultadosimple?cadena=…` | none | The best legislation API in LatAm. Consolidated XML (EsquemaIntercambioNorma) with per-article structure. |
| Colombia | C (Corte Constitucional relatoria HTML) + A (datos.gov.co Socrata, metadata only) | C (Secretaría Senado basedoc HTML, Función Pública gestor normativo); SUIN is an Angular SPA | `www.corteconstitucional.gov.co/relatoria/{yyyy}/{T-001-24}.htm` | none | No official full-text search API found. Consejo de Estado and CSJ not probed (unverified). |
| Peru | D (PJ jurisprudencia 403 WAF) | D/C (SPIJ timed out; El Peruano JS challenge) | – | – | Nothing usable from abroad. TC (tc.gob.pe) is a WordPress site, HTML only. |
| Uruguay | C (BJN — JSF/Seam forms, POST + viewstate) | **A** (IMPO `?json=true` on any norm/article URL) | `www.impo.com.uy/bases/leyes/{num}-{year}?json=true`; `/bases/codigo-civil/16603-1994/{art}?json=true` | none | IMPO JSON comes back as ISO-8859-1. Per-article access works. |
| Costa Rica | C (Nexus PJ, SPA) | C (SCIJ → sinalevi.go.cr HTML) | `pgrweb.go.cr/scij/...nrm_texto_completo.aspx?nValor2={id}` → redirects to sinalevi | none | The most promising in Central America, but no documented API (unverified). |
| Rest of Central America | D/C (unverified) | C (official gazettes as PDF) | – | – | Not probed in depth. Expect PDF gazettes only. |
| Caribbean (CCJ) | C (WordPress REST works; judgments are PDFs) | – | `ccj.org/wp-json/wp/v2/posts` | none | CCJ judgments are PDF attachments. |
| Caribbean (CariLII) | **D** | – | – | – | `carilii.org` does not resolve; `www.carilii.org` timed out. Looks dead. CommonLII's Caribbean Law Project (AustLII) is the remaining free option, HTML. CariLaw (UWI/vLex) is paid. |

---

## United States

### Case law

**CourtListener (Free Law Project)** — `https://www.courtlistener.com/api/rest/v4/`
- Coverage: all federal courts plus state appellate/supreme courts (about 10M opinions), PACER/RECAP dockets, judges, citation graph. Absorbed the CAP corpus.
- Endpoints: `/search/?q=…&type=o` (opinions, ES full-text), `type=r` (RECAP), `/opinions/{id}/`, `/clusters/`, `/dockets/`, `/courts/`, `/citation-lookup/` (POST text → resolved cites).
- **Auth (verified 2026-11-05):** `/search/` and `/opinions/` return `401 Authentication credentials were not provided` without a token. v3 returns `403 Anonymous users don't have permission`. `/courts/` still answers anonymously.
- **Rate limits (official wiki, wiki.free.law):** authenticated free accounts get **5 req/min, 50/hour, 125/day** (rolling, all concurrent). That is far too low for a shared public MCP. Each user must bring their own token, and even then 125/day is tight. Higher limits need membership or a commercial agreement.
- Header: `Authorization: Token <key>`. Licence: data is public domain / CC0 for the content FLP creates. HTML opinion pages return `202` (bot interstitial). robots.txt says "contact us before crawling". → **Tier B (key, low quota).**

**govinfo USCOURTS collection (GPO, official)** — `https://api.govinfo.gov/`
- Federal appellate, district and bankruptcy court opinions, about 2004 onward (verified count: 114,569 hits for `qualified immunity`).
- `POST /search?api_key=…` with body `{"query":"collection:USCOURTS qualified immunity","pageSize":10,"offsetMark":"*"}` → packageId/granuleId. Then `GET /packages/{packageId}/granules/{granuleId}/summary`, then the `download.txtLink`/`pdfLink`.
- Auth: api.data.gov key (free, instant). `DEMO_KEY` worked (verified 2026-11-05) but has a tiny quota. Normal keys get about 1,000 req/hour (api.data.gov default, unverified for govinfo specifically).
- No SCOTUS (use supremecourt.gov slip opinions HTML/PDF or CourtListener). → **Tier B.** The best official full-text federal source.

**Caselaw Access Project (Harvard LIL)** — `https://static.case.law/`
- All official US reporters to about 2018 (6.7M cases). CC0. The API and search at api.case.law were retired in 2024. What remains is static: `/{reporter}/{volume}/cases/{page}-{n}.json` plus per-volume zip/tar/PDF. Verified 2026-11-05: `static.case.law/us/1/cases/0001-01.json` returns JSON (name, decision_date, citations, casebody).
- `CasesMetadata.json` at the reporter level returned 404. Use the HTML index listing.
- No search, so it is only useful for get-by-citation (map `1 U.S. 1` → `us/1/cases/0001-01.json`, via page number). → **A for fetch, nothing for search.**

**Other:** supremecourt.gov (HTML/PDF slip opinions, reachable). PACER is paid (D). Most state courts are HTML/PDF only.

### Legislation

**eCFR (Code of Federal Regulations, consolidated daily)** — `https://www.ecfr.gov/api/`
- `GET /api/versioner/v1/titles.json` (verified: up_to_date_as_of 2026-11-03).
- `GET /api/search/v1/results?query=…&per_page=…` → full-text search returning hierarchy (title/part/section) (verified).
- `GET /api/versioner/v1/full/{date}/title-{N}.xml?part=…&section=…` → **single-section XML**. **Gotcha: you must send `Accept-Encoding: gzip`, otherwise you get a 406 "requires response compression"** (verified).
- Point-in-time by date. No key. Public domain. → **Tier A.**

**Federal Register** — `https://www.federalregister.gov/api/v1/documents.json?conditions[term]=…` returns JSON. No key (verified; 2,019 hits for "hipaa"). → **A.**

**US Code (OLRC)** — `https://uscode.house.gov/`
- **The site was redesigned. The old `view.xhtml?req=granuleid:USC-prelim-title42-section1983` URLs now return "Page Not Found", and `search.xhtml` returns 403 (Akamai).** Verified 2026-11-05.
- New per-section HTML: `https://uscode.house.gov/us/usc/t42/s1983/` (trailing slash; without it you get a 301). Verified: current through Pub. L. 119-136 (2026-10-22), with notes.
- Bulk USLM XML per title on `/download.html`. No search API. → **C/A** (static HTML per section, identifier = title + section).
- Alternative: govinfo `USCODE-{year}-title{N}` packages/granules (verified, B), annual edition only, so it lags.

**Congress.gov API** — `https://api.congress.gov/v3/bill?api_key=…&format=json` (verified with DEMO_KEY). Bills, laws, amendments, CRS reports. Bill text links go to govinfo. → **B.**

**States:** Open States `v3.openstates.org` (403 without `X-API-KEY`, verified) gives bills/legislators for all 50 states + DC + PR, not codified statutes. LegiScan (key, free tier, 30k queries/month per its docs, unverified). Consolidated state codes: per-state HTML (C), with varying ToS. Some (e.g., Georgia/Oregon) have a history of copyright claims over annotated codes.

### Existing MCPs / libraries (don't duplicate)
- CourtListener: `blakeox/courtlistener-mcp` (MIT, ★16, active Oct 2026), `cyanheads/courtlistener-mcp-server` (Apache-2.0, active Nov 2026), `DefendTheDisabled/courtlistener-mcp` (MIT), `Vaquill-AI/courtlistener-mcp` (MIT, hosted, includes eCFR), `khizar-anjum/courtlistener-mcp`. FLP's own Python client `freelawproject/courtlistener-api-client` (unverified name).
- eCFR: `lrehmann/ecfr-mcp` (MIT), `AI4RA/mcp-ecfr`, `SidneyAnderson/ecfr-mcp`, `ctrimm/ecfr-mcp-safety-net`.
- US Code: `lrehmann/uscode-mcp` (MIT), `jds2001/uscode-mcp`.
- govinfo: `Travis-Prall/govinfo-mcp`, `artvandelay/govinfo-mcp`.
- Congress.gov: `AshwinSundar/congress_gov_mcp` (MIT, ★19).
- Federal Register: `VeronaStrategic/federal-register-mcp` (MIT, no key), `QuentinCody/federal-register-mcp-server`, `aml25/federal-register-mcp`, others.
- States: `sh-patterson/legiscan-mcp` (MIT, ★12), `cyanheads/openstates-mcp-server` (Apache-2.0).
- **Verdict:** the US is saturated. A world MCP should wrap thin adapters (govinfo + eCFR + uscode HTML + CourtListener with user-supplied token), not compete.

---

## Canada

### Case law
**A2AJ Canadian Legal Data API (York U / Osgoode, Sean Rehaag)** — `https://api.a2aj.ca/` (OpenAPI at `/openapi.json`, docs `/docs`), hosted MCP at `https://mcp.a2aj.ca/mcp`
- `GET /search?query=…&doc_type=cases|laws&search_type=&size=&search_language=&sort_results=&dataset=SCC,ONCA&start_date=&end_date=` → full-text (Elasticsearch). Verified 2026-11-05.
- `GET /fetch?citation=2022 SCC 12&doc_type=cases&output_language=en&section=&start_char=&end_char=&include_citations=` → full text with char-range paging. Verified.
- `GET /coverage?doc_type=cases|laws`. Verified: **31 case datasets** (SCC 1877–, FC, FCA, TCC, ONCA, BCCA, BCSC, NSCA/NSSC/NSPC/NSSM/NSFC, NLCA, YKCA, CMAC, CHRT, CIRB, CITT, RAD/RPD/RLLR (IRB), SST, TMOB, FPSLREB, etc.) and **26 legislation datasets** (federal + all provinces/territories, statutes and regs).
- No key. Bilingual EN/FR. **Not official**: weekly mirror from HuggingFace datasets `a2aj/canadian-case-law`, `a2aj/canadian-laws`. Each record carries `upstream_license` (e.g., SCC: non-commercial restrictions, "unofficial reproduction"). Self-hostable: `a2aj-ca/a2aj-api-public` (MIT). → **Tier A\***.
- Gotcha: no ONSC, QC courts, AB/SK/MB courts. Those sit on CanLII only.

**CanLII API** — `https://api.canlii.org/v1/` (`caseBrowse`, `caseCitator`, `legislationBrowse`)
- Key only by request via the CanLII feedback form. **Metadata only, no decision text** (official docs on GitHub `canlii/API_documentation`). Without a valid key you get `403 ACCESS_DENIED` (verified).
- canlii.org HTML is behind a JS challenge ("Please enable JS", verified), and CanLII's terms prohibit scraping. → **B for metadata, D for text.**

**SCC (Lexum)** — `https://decisions.scc-csc.ca/scc-csc/scc-csc/en/item/{id}/index.do` (HTML, verified) and RSS `…/scc-csc/en/rss.do` (verified). Item IDs are not citations. Map via A2AJ's `url_en`. → C.

### Legislation
**Justice Laws (federal, official, consolidated)** — `https://laws-lois.justice.gc.ca/`
- Index: `/eng/XML/Legis.xml` (all acts and regs with XML links, verified).
- Whole-document XML: `/eng/XML/C-46.xml` (Criminal Code; `lims:pit-date`, `lims:lastAmendedDate` attributes), `/eng/XML/SOR-2002-227.xml` (verified). Sections live inside the XML (`<Section>` with `lims:id`).
- Per-section HTML: `/eng/acts/C-46/section-718.html` (verified). French: `/fra/XML/…`. Point-in-time versions exist. Open Government Licence – Canada. No key. → **A.**
- Gotcha: the Criminal Code XML is several MB. Fetch once per call and slice; don't page it.

**Provinces:** BC Laws CiviX API `https://www.bclaws.gov.bc.ca/civix/search/complete/fullsearch?q=…&s=0&e=10&nFrag=&lFrag=` (XML full-text, verified, 162 hits for "tenancy") + `/civix/document/id/complete/statreg/{id}/xml` (verified). Queen's Printer Licence BC → **A**. Ontario e-Laws `ontario.ca/laws/statute/90h08` is a JS app (C). LegisQuébec returned an error page to curl (unverified). All provinces are also covered by A2AJ (A\*).

### Existing MCPs
- `a2aj-ca/a2aj-api-public` (MIT; official A2AJ API + MCP, hosted).
- CanLII: `Alhwyn/canlii-mcp` (MIT, ★28, active), `Vaquill-AI/canlii-mcp` (MIT, hosted), `tomilashy/canlii-mcp`, `khnxx/canlii-mcp`, `donna49/canlii-mcp`, `yvesnormandin/canlii_mcp_server`. All need a CanLII key and are metadata-only.
- Bulk data: `a2aj-ca/canadian-legal-data` (★53).

---

## Mexico
- **SCJN Semanario Judicial (tesis/jurisprudencia):** internal JSON API `https://sjf2.scjn.gob.mx/services/sjftesismicroservice/api/public/tesis` (POST search with classifiers `idEpoca`, `numInstancia`, `tipoDocumento`, `searchTerms`), `/tesis/{ius}`, `/health`. Known from `magiobus/scjn-tesis-api-` (MIT Node client, about 74k tesis). **Verified 2026-11-05: `/health` → `403 {"error":"Acceso denegado: Formato inválido."}` and `/tesis/{id}` → Incapsula JS challenge.** The site is now WAF-protected, so a plain-HTTP client fails. → **D** (would need a headless browser).
- **SCJN Buscador Jurídico (sentencias)** `bj.scjn.gob.mx` (+ `/datos-abiertos`) and `bicentenario.scjn.gob.mx`: all return a 302 "Loading" cookie challenge (verified). Open-data API claimed by SCJN transparency docs, unverified.
- **Legislation:** Cámara de Diputados `diputados.gob.mx/LeyesBiblio/` (consolidated federal laws, PDF/DOC/HTML `ref/{ley}.htm`) — **connection timed out from the UK (verified, probably geo/ASN filtering)**. DOF `dof.gob.mx` homepage reachable (HTML). The SIDOF JSON (`sidofqa.segob.gob.mx/dof/sidof/notas/{date}`) returns `400 BAD_REQUEST` (format unknown). SCJN `legislacion.scjn.gob.mx` (federal + state laws, ASP.NET) reachable (C).
- MCPs: none found for SCJN. `magiobus/scjn-tesis-api-` (client), `IntersectaOrg/amicus_scjn_ppo` (old).
- Tier: case law **D**, legislation **C** (and only if reachable in-country).

## Brazil
- **STF jurisprudência** — `POST https://jurisprudencia.stf.jus.br/api/search/search` with an Elasticsearch-style body `{"query":{"bool":{"must":[{"query_string":{"query":"habeas"}}]}},"size":1}` → JSON hits from `jurisprudencia-idx…` (base `acordaos`, `titulo`, `ministro_facet`…). **Verified 2026-11-05, no key.** Undocumented internal API, so it may break. ToS unverified. → A\*.
- **STJ SCON** `scon.stj.jus.br/SCON/pesquisar.jsp?livre=…` → HTML reachable (C).
- **CNJ DataJud** `https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search` (ES; public APIKey published on the CNJ wiki). Process metadata/movements, **not decision text**. **Timed out from the UK** (verified). DJEN `comunicaapi.pje.jus.br` → CloudFront 403 geo-block (verified). → D from abroad, A in-country.
- **Legislation:** Planalto `planalto.gov.br/ccivil_03/...compilado.htm` (consolidated, HTML) → **"Acesso Negado" from the UK (verified)**. LexML URN resolver `https://www.lexml.gov.br/urn/urn:lex:br:federal:lei:1990-09-11;8078` → HTML metadata page (verified). LexML SRU search `lexml.gov.br/busca/SRU?operation=searchRetrieve&query=…` → Senado "Verificação de segurança" WAF challenge (verified). Senado Dados Abertos `legis.senado.leg.br/dadosabertos/legislacao/lista?tipo=LEI&ano=2024` (JSON/XML, verified, but **slow (>60 s) and intermittently 503**). normas.leg.br (new Senado/Câmara portal, Angular) exposes `/api/public/normas` (returns 400 with my params; params unverified). Identifier: LexML URN (`urn:lex:br:federal:lei:AAAA-MM-DD;NUM`).
- MCPs/libraries (crowded): `DeHor-Labs/mcp-juridico-brasil` (MIT, ★127), `brunoflma/jurisprudenciaia-mcp` (★18), `mcp-dir/jurisprudencia-mcp` (MIT, 17 courts), `robertogecia/trf1-jurisprudencia-mcp` (MIT), `netoferraz/py-lexml-acervo` (GPL-3, LexML client), `rvsanches/skills-datajud-djen` (MIT), `lexml/*` (official parsers, GPL-2).
- Tier: case law A\* (STF) / C (STJ), legislation C/D (abroad).

## Argentina
- **SAIJ** (Ministerio de Justicia; jurisprudence summaries + full decisions, national + provincial legislation, doctrina): `GET https://www.saij.gob.ar/busqueda?o={offset}&p={size}&f=Total|Tipo de Documento|Fecha|Organismo|Publicación|Tema|Estado de Vigencia|Autor|Jurisdicción&s=&v=colapsada&r={query}` → JSON (`searchResults.documentResultList[].documentAbstract` is a JSON string). Verified 2026-11-05. **Gotchas:** stems aggressively (`despido`→`despid`); field prefixes `titulo:`, `texto:` work; a bare query like `ley 20744` returned 0; malformed `f`/`s` returns 500; `totalSearchResults` looks unreliable. Docs: `view-document?guid=…`. → A\* (official but undocumented).
- **Infoleg** `servicios.infoleg.gob.ar/infolegInternet/anexos/…/texact.htm` → redirects to `mostrarArchivoInexistente.do` (verified, broken links). Successor: `argentina.gob.ar/normativa/nacional/{slug}/actualizacion` (HTML, 200). Consolidated text is not cleanly parseable. → C.
- CSJN: `sj.csjn.gov.ar` (not probed, unverified). CSJN has an open-data portal (per news).
- MCPs: `abenassi/argentina-data-mcp` (★7, Infoleg+BCRA+AFIP), `crivaronicolini/infolegAI` (GPL-3), `datos-justicia-argentina/Base-de-datos-legislativos-infoleg` (dataset).

## Chile
- **BCN Ley Chile (official, consolidated)**: `GET https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma=172986` → full XML (`EsquemaIntercambioNorma-v1-0.xsd`, `derogado`, `fechaVersion`, structured articles). Verified. Search: `GET https://nuevo.leychile.cl/servicios/Consulta/listaresultadosimple?cadena=trabajo&exacta=0&tipoviene=1&cantidad=10&page_num=1` → JSON (verified, Código del Trabajo top hit). Identifier: `idNorma`; historical versions via `idVersion`/`fechaVersion`. No key. → **A.**
- **Poder Judicial** `juris.pjud.cl/busqueda?Corte_Suprema` → HTML/JS (reachable, `noindex`). JSON search is behind a CSRF token (unverified). → C.
- MCPs: `IanGuiloff/LeyChile-mcp` (★3, live BCN), `diegocaro/leychile` (MIT client), `diegocaro/leychile-texto`.

## Colombia
- **Corte Constitucional** relatoria: `https://www.corteconstitucional.gov.co/relatoria/{yyyy}/{T-001-24}.htm` (+ `.rtf`), verified HTML. Metadata of all sentencias since 1992 as a Socrata dataset: `https://www.datos.gov.co/resource/v2k4-2t8s.json?$limit=…&$where=…` (verified, SoQL, no key, no text). → C + A (metadata).
- Consejo de Estado, Corte Suprema (CSJ relatoría): not probed, unverified.
- **Legislation:** Secretaría del Senado `secretariasenado.gov.co/senado/basedoc/ley_1437_2011.html` (consolidated-ish HTML, verified), Función Pública Gestor Normativo `funcionpublica.gov.co/eva/gestornormativo/norma.php?i={id}` (HTML, verified), SUIN-Juriscol `suin-juriscol.gov.co/viewDocument.asp?id=…` now an Angular SPA (verified). → C.
- MCPs: none found.

## Peru
- PJ `jurisprudencia.pj.gob.pe` → **403 WAF** (verified). SPIJ (MINJUS legislation) `spij.minjus.gob.pe` → **timed out** (verified). El Peruano `busquedas.elperuano.pe` → JS obfuscation challenge (verified). TC `tc.gob.pe` → WordPress (reachable, HTML/PDF). → **D** (C for the TC only).
- MCPs: none found.

## Uruguay
- **IMPO (official consolidated legislation)**: append `?json=true` to any norm URL. `https://www.impo.com.uy/bases/leyes/19889-2020?json=true` (whole law metadata + articles) and per-article `https://www.impo.com.uy/bases/codigo-civil/16603-1994/1?json=true` (verified). **Gotcha: the response is ISO-8859-1, so decode explicitly.** Identifier: `{base}/{num}-{year}/{article}`. → **A.**
- **BJN** (Base de Jurisprudencia Nacional) `bjn.poderjudicial.gub.uy/BJNPUBLICA/busquedaSimple.seam` → JSF/Seam, stateful POST with viewstate (reachable). → C (painful).

## Central America & Caribbean (sweep)
- **Costa Rica**: SCIJ/SINALEVI `pgrweb.go.cr/scij/...nrm_texto_completo.aspx?nValor1=1&nValor2=871` → redirects to `sinalevi.go.cr/ResultadosNormativa/Informacion?param1=871…` (HTML, verified). Nexus PJ `nexuspj.poder-judicial.go.cr` (case law, SPA; guessed `/api/search` 404). C for both. Best candidate in the region.
- Guatemala, Honduras, El Salvador, Nicaragua, Panama, Dominican Republic: not probed. Expect gazette PDFs and court-site HTML (unverified, C/D).
- **Caribbean Court of Justice**: `ccj.org/wp-json/wp/v2/posts` WordPress REST works (verified). Judgments are PDF attachments. → C.
- **CariLII**: `carilii.org` does not resolve and `www.carilii.org` timed out (verified 2026-11-05). Treat it as dead (D). Fallbacks: CommonLII "Caribbean Law Project" (AustLII-run HTML, sparse; AustLII forbids bulk robots, unverified) and CariLaw (UWI + vLex, **paid**, D).
- **Puerto Rico**: covered by CourtListener (`pr`, `prapp`), unverified depth.

## Cross-cutting gotchas
1. **Geo-blocking is the #1 LatAm problem.** Planalto, DataJud, DJEN, diputados.gob.mx, SPIJ and PJ Peru all failed from a UK IP. A "live fetch" MCP is only as good as the user's IP. Document this, and consider an optional proxy setting.
2. **WAF/JS challenges** (Incapsula on SCJN, Senado/LexML, CanLII, El Peruano) break plain `httpx`. Don't build on them.
3. **CourtListener quota (125/day free)** means it cannot be the default US search backend. Use govinfo USCOURTS (api.data.gov key, ~1,000/h) for federal full-text, and CourtListener only with the user's own token.
4. **A2AJ** is the single highest-value find. One no-key API gives Canadian full-text case law and all provincial legislation, plus a hosted MCP. Respect each record's `upstream_license` (several courts are non-commercial).
5. Best no-key official legislation APIs in the region: **eCFR, Justice Laws XML, BC Laws, BCN Ley Chile, IMPO Uruguay.**
