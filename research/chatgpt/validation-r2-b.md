# Validation of ChatGPT's r2_b.md ranked shortlist — 2026-11-07

Method: every claim treated as a lead. Live requests made with the repo client (`world_legal_mcp._http`),
UA `Fontes/0.1.0 (+https://github.com/ykarapazar/fontes)`, a handful of requests per site, ≥1.5 s apart.
No sign-ups, logins, header/UA changes or bot-check bypass. Nobody was contacted. "No terms found" means
no terms page was found. It does not mean permission was given.

## 1. jm — Jamaica Legal Information Portal (LIPJ) — **NEEDS-PERMISSION**
- Reachable: yes, `https://lipj.gov.jm` returns 200 (nginx).
- Listing: `GET /cms/api/records?pagination[pageSize]=1&populate[sourceFile]=true` gives `total` 17963.
- Search: works, though ChatGPT did not check it. Strapi filter `GET /cms/api/records?filters[shortTitle][$containsi]=Arbitration&pagination[pageSize]=5&fields[0]=shortTitle&populate[document][fields][0]=longTitle&populate[document][fields][1]=operationalDate` returns total 14, including id 74874 "The Arbitration Act" (operationalDate 2017-07-07).
- Document: `GET /cms/api/records/74874?populate[ocr]=true&populate[sourceFile]=true&populate[document]=true` returns 35 OCR pages: "THE ARBITRATION ACT Act 13 of2017. [7th July,2017.] PARTI Preliminary 1.This Act may be cited as the Arbitration Act Short title." This is OCR of scans: margin notes are mixed into the text, and there are spacing and OCR errors. Record 82613 confirmed. Its `document.longTitle` holds the full title "The Toll Roads (Approved Location of Tyre Deflation Devices) Notice,2013". The source PDF under `/uploads/…` timed out (ReadTimeout).
- Terms: Terms of Use (CMS `/cms/api/pages/319`, effective 25 July 2025, MLCA). §3: "You agree to use JLIP services—including AI chatbot, legal repository, and community forum—only for lawful, non-commercial purposes." §6: "All official legal documents are public domain. However, the JLIP website's layout, platform features, software architecture, and design assets are the property of the Government of Jamaica or licensed partners. You may not reproduce, republish, or exploit any portal functionality without prior written consent."
- robots (`https://lipj.gov.jm/robots.txt`): `User-agent: *`, empty `Disallow:`. The sitemap is on a third-party vendor domain (`https://api.drawmet.site/api/sitemap/index.xml`).
- Coverage: about 18k records (acts, regulations, notices). The text is OCR, not born-digital.
- Verdict reason: the texts are public domain, but automated use of the API looks like "exploit any portal functionality" and needs written consent. §3 also says non-commercial only.
- ChatGPT errors: left out the second half of §6 (no exploiting portal functionality without consent).

## 2. rs — National Assembly of Serbia (adopted laws) — **GO-WITH-CAVEAT**
- Reachable: yes (Apache).
- Listing: `/akti/doneti-zakoni/doneti-zakoni.1033.html` is one ~1 MB page with 395 rows (2024: 91, 2025: 179, 2026: 125), covering 23 Apr 2024 – 31 Aug 2026 (14th convocation). Each row links PDF/DOC files of the law and the bill.
- Search: `POST https://www.parlament.gov.rs/narodna-skupstina-.872.html` with form `type=regulation&SearchText=sudijama&category_id=5` returns 200 with 20 hits. These include older convocations (paths dated 2009, 2010, 2015, 2017, 2020, 2021, 13_saziv).
- Document: PDF 2445-26 has a text layer: "Z A K O N O IZMENI ZAKONA O SUDIJAMA Član 1. U Zakonu o sudijama („Službeni glasnik RS”, br. 10/23, 9/26 i 56/26), član 51. menja se i glasi:".
- Terms: none found. The footer says only "© 2011 Narodna skupština Republike Srbije".
- robots (`https://www.parlament.gov.rs/robots.txt`): disallows `/*.html.html`, info-tabla, `/upload/archive/files/{lat,cir,eng}/*.txt$`, `/upload/contactdocs/`. Law PDFs are not disallowed.
- Coverage: laws as passed (amending acts), not consolidated texts.
- ChatGPT errors: none found. ChatGPT understated it: search exists and reaches back to 2009.

## 3. cl — Tribunal Constitucional de Chile (buscador API) — **GO-WITH-CAVEAT**
- Reachable: yes. `buscador-backend.tcchile.cl` responds. `www.tcchile.cl` meta-redirects to `www1.tribunalconstitucional.cl`.
- Search: `GET https://buscador-backend.tcchile.cl/api/extended/sentencias?filter={"search":"constitucion"}` gives count 95, 5 per page, with fields rol, sentence_id, competencia and full-text `content`. `filter={"search":"propiedad"}` gives count 5084.
- Document: `GET /api/extended/8525/download` (by rol/folio, the same call the frontend makes) returns application/pdf, 7 pages with an OCR text layer: "TRIBUNAL CONSTITUCIONAL DE CHILE Sentencia Rol 8525-2020 CPR [20 de marzo de 2020] CONTROL DE CONSTITUCIONALIDAD DEL PROYECTO DE LEY QUE CREA UN SUBSIDIO…" (with OCR errors such as "Constitucién"). Metadata comes from `GET /api/buscadorexterno/ficha/8525` (fecha_sentencia 2020-03-20, exist_file 1). Using `sentence_id` (29622) instead returns 404 "No se encontró un documento con el título: 29622".
- Terms: none found on either site.
- robots: `https://buscador-backend.tcchile.cl/robots.txt` and `https://www1.tribunalconstitucional.cl/robots.txt` both have `User-agent: *` with empty `Disallow:`. The frontend robots returns 404.
- Note: the frontend JS bundle contains a third-party document-store token. It was not used, and Fontes must not use it.
- Coverage: constitutional rulings, full text, apparently back many years (count 5084 for "propiedad").
- ChatGPT errors: said the document/download routes were "not verified working". They work when called with the rol (ChatGPT used the wrong id).

## 4. ru — Sudact (sudact.ru), UNOFFICIAL — **NO**
- Reachable: yes. Document `/vsrf/doc/QvaoO2KNOaT/` returns full HTML text: "ВЕРХОВНЫЙ СУД РОССИЙСКОЙ ФЕДЕРАЦИИ № 310-ЭС25-14430(3) ОПРЕДЕЛЕНИЕ г. Москва 30 октября 2026 г. … определил: отказать ФИО1 в передаче кассационной жалобы…".
- Search: the form GET `/vsrf/doc/?vsrf-txt=…` returns only an empty page shell. Results are loaded by `main.js` from `'/'+form+'/doc_ajax/'+location.search`, and robots disallows that path. The only robots-compliant access is the listings (`/vsrf/`, ~30 doc links) and the sitemaps, so there is no compliant search.
- robots (`https://sudact.ru/robots.txt`, `User-Agent: *`): disallows `/vsrf/doc_ajax/`, `/regular/doc_ajax/`, `/arbitral/doc_ajax/`, `/magistrate/doc_ajax/`, the print views and `/defence/check_captcha/`, among others.
- Terms: no terms of use found. `/about/` says "Бесплатный и надежный доступ для всех пользователей ко всем судебным актам." The footer says "Все права защищены © 2012-2026 «Судебные и нормативные акты РФ»". The privacy policy (`/politic/`, 01.02.2025) names no operator (no company, no ИНН). The site carries Yandex AdFox ads.
- Verdict reason: search only works through robots-disallowed endpoints, "all rights reserved", anonymous operator.
- ChatGPT errors: did not notice that search results come only from the robots-disallowed `doc_ajax`. It also quoted a `/*/doc_ajax/` wildcard that does not exist; the real lines are per section (minor, counted with the first point).

## 5. ec — Asamblea Nacional (leyes aprobadas) — **NO** (for current laws)
- Reachable: yes.
- Listing/search: `/es/leyes-aprobadas` shows ~15 rows per page, with a pager to page=22 (~340 laws) and period filters from 2009-2013 to 2025-2029. A title filter works: `GET /es/leyes-aprobadas?leyes-aprobadas=All&title=aviación&fecha=` returns 3 rows (Ley Orgánica de Aviación Civil, R.O. 382 2026; 2019; 2018).
- Document: older files have text, e.g. `ro_ley_defensoria_del_pueblo.pdf` (12 pages, 73k chars: "Art. 1.- Objeto.- Esta Ley tiene como objeto establecer a la Defensoría del Pueblo…"). Current gazettes are scans: `ro_40.pdf` has 21 pages and only 3 with >300 chars (the law pages carry only a ~74-char header). `ro_38.pdf` has 139 pages and 6 with text.
- Terms: none found.
- robots (`https://www.asambleanacional.gob.ec/robots.txt`): `Crawl-delay: 1`. Disallows `/search/`, `/node/`, `/?q=`, `/documents/` and admin paths. `/es/system/files/` is allowed.
- Coverage: about 340 laws from 2009. Recent ones are image-only and would need OCR.
- ChatGPT errors: ranked it on "verified text-bearing enacted-law PDFs", but its sample was a 2019 PDF. The 2026 gazette law pages are image scans, which the repo's ec.py already recorded.

## 6. li — Fürstlicher Oberster Gerichtshof (ogh.li archive) — **GO-WITH-CAVEAT**
- Reachable: yes. robots `https://www.ogh.li/robots.txt` returns 404 (no rules).
- Listing: `/entscheidungen-des-ogh` lists 63 PDFs by default (2025: 44, 2024: 18). The year selector offers 1999–2025. An ASP.NET POST (`__VIEWSTATE`/`__EVENTVALIDATION` plus `ctl00$content$ddYears=2005&search=&submit=Filtern`) returns 336 PDFs, but their decision dates are 2020–2025 (plus one from 2009). Picking an old year does not bring back old decisions. A text search field exists (`search=`) but was not tested with a query.
- Document: `17-va-2024-125-ogh-2025-74.pdf` has 36 pages of text: "17 VA.2024.125 OGH.2025.74 B E S C H L U S S Der Fürstliche Oberste Gerichtshof als Revisionsrekursgericht…" (anonymised).
- Terms: Impressum `https://www.ogh.li/impressum`: "Sämtliche Texte, Tabellen, Grafiken, Filme und Bilder sind urheberrechtlich geschützt. Eine kommerzielle Nutzung bedarf der vorhergehenden schriftlichen Genehmigung."
- Coverage: about 336 OGH decisions, 2020–2025. The successor portal (gerichtsentscheidungen.li) is disallowed by robots.
- Verdict reason: usable non-commercially. Commercial use needs written permission. The archive is frozen.
- ChatGPT errors: none counted. Its claim that the judiciary site calls ogh.li "the archive for 2020–2025" could not be reproduced (unverified), but the coverage it gave matches.

## 7. cr — Tribunal Supremo de Elecciones (jurisprudencia) — **GO-WITH-CAVEAT**
- Reachable: yes. No challenge was served in this run (every request returned 200 with content). The pages do embed Radware Bot Manager (`stormcaster.js`, `validate.perfdrive.com`), so challenges can appear. Fontes must stop on any challenge.
- Search: `GET https://www.tse.go.cr/juris/search.asp?zoom_query=deuda+politica` returns "470 resultados" (electorales 290, municipales 5, relevantes 175), 10 per page.
- Bulk: `juris_anual.html` lists 103 ZIPs, electoral from 1946 to 2026 and municipal from 1975.
- Document: `/imgs/info/4190-E8-2025.pdf` has 15 pages of text: "N.° 4190-E8-2025.-TRIBUNAL SUPREMO DE ELECCIONES. San José, a las trece horas con treinta minutos del veinte de junio de dos mil veinticinco."
- Terms (`https://www.tse.go.cr/terminos_condiciones_uso.html`): "El acceso al sitio es gratuito y no genera relación comercial…". A trademark clause bars reproducing logos, name or graphics without written permission. Nothing on automation or AI. The footer links CC BY-SA 4.0: "Basada en una obra en https://www.tse.go.cr".
- robots (`https://www.tse.go.cr/robots.txt`): disallows `/cgi-bin/`, `/images/`, `/tmp/`, `/private/` and similar. `/juris/` and `/imgs/info/` are not disallowed.
- Coverage: electoral case law only.
- ChatGPT errors: none counted. Its claim that Radware served a captcha was not reproduced, but this is plausibly intermittent.

## gt — Corte de Constitucionalidad, case-law "repair" — **GO-WITH-CAVEAT** (already built; search UNVERIFIED)
- Document: `https://jurisprudencia.cc.gob.gt/Sentencias/850297.3670-2022.pdf` has 20 pages of text: "EXPEDIENTE 3670-2022 CORTE DE CONSTITUCIONALIDAD: Guatemala, veinticuatro de agosto de dos mil veintidós."
- robots (`https://jurisprudencia.cc.gob.gt/robots.txt`, Cloudflare-managed): `Content-Signal: search=yes,ai-train=no,use=reference`, `Allow: /` for `*`. Named AI crawlers (ClaudeBot, GPTBot, anthropic-ai…) get `Disallow: /`. The Fontes UA is not named.
- Search: `/sjc/` returns 200 without a challenge. It is a DevExpress ASP.NET app ("Sistema de Consulta de Jurisprudencia Constitucional") with expediente and text search, all through DevExpress callbacks. This was not tested, so it is only a lead.
- Landmark list: 36 entries, 1991 (290-91/292-91) to 2014. ChatGPT got this right.
- ChatGPT errors: presented direct PDF fetching as the repair, but `gt.py` already fetches decisions from `/Sentencias/<stem>.pdf`. The missing piece (search) is still unresolved.

## Holds (one-line status)
- **is — Alþingi law collection: NO (blocked).** `https://www.althingi.is/lagas/158a/1940019.html` returned 403 with a Cloudflare "Just a moment..." challenge. It was not bypassed. robots (`Crawl-delay: 5`) points automated users to the XML open-data service `https://www.althingi.is/altext/xml/`, which returned 200 unchallenged. That service covers parliamentary data; whether it includes consolidated law text is unverified.
- **do — Consultoría Jurídica del Poder Ejecutivo: NO for now.** `https://www.consultoria.gov.do/robots.txt` is permissive: Allow `/`, disallows only dashboard, `/api/auth/` and `/api/admin/`. `/terminos` loads (200) and says "Los textos legales, decretos, resoluciones y gacetas publicadas en este portal son documentos de dominio público". It also says: "Se prohíbe el uso de robots, scripts automatizados o técnicas de extracción no autorizada (scraping) que degraden el rendimiento de los servicios". `GET /api/consultas/search` returns 404 JSON. No challenge was served this time; the repo's record of a Cloudflare managed challenge was not reproduced. A working search endpoint was not found.

## Summary

| Source | Verdict | One-line reason |
|---|---|---|
| jm LIPJ | NEEDS-PERMISSION | API and search work, but the text is OCR; terms say non-commercial and "may not … exploit any portal functionality without prior written consent" |
| rs National Assembly | GO-WITH-CAVEAT | Text PDFs, working POST search back to 2009; as-passed laws only, no terms found |
| cl Tribunal Constitucional | GO-WITH-CAVEAT | Full-text search API plus PDF download by rol work; OCR quality, no terms found |
| ru Sudact (unofficial) | NO | Search only through robots-disallowed `doc_ajax`; "all rights reserved"; anonymous operator |
| ec Asamblea Nacional | NO | Listing and title filter work, but 2026 law gazettes are image scans |
| li OGH archive | GO-WITH-CAVEAT | Text PDFs 2020–2025, frozen; commercial use needs written permission |
| cr TSE | GO-WITH-CAVEAT | Search, bulk ZIPs and text PDFs work, CC BY-SA footer; Radware present, stop on any challenge |
| gt CC repair | GO-WITH-CAVEAT | PDF fetch already implemented; search via the SJC callbacks unverified |
| is Alþingi | NO (blocked) | Cloudflare challenge on law pages; XML open-data service is a lead, unverified for law text |
| do Consultoría | NO (for now) | Terms ban scraping that degrades service; no search endpoint found |

**ChatGPT errors found: 5**
1. cl: said the document/download routes were "not verified working". `/api/extended/<rol>/download` returns the PDF.
2. jm: left out the terms §6 clause "may not reproduce, republish, or exploit any portal functionality without prior written consent".
3. ec: ranked on "verified text-bearing" PDFs using a 2019 sample. The current (2026) gazette law pages are image-only.
4. ru: did not notice that search results come only from robots-disallowed `/…/doc_ajax/`, and misquoted that rule as a `/*/doc_ajax/` wildcard.
5. gt: presented direct PDF fetching as a new repair. `gt.py` already does this. The real gap (search) is unaddressed.

Not counted as errors: the cr Radware captcha (not reproduced, plausibly intermittent); the li "archive for 2020–2025" attribution (unverified, but the coverage matches); the do Cloudflare challenge (not served this run, plausibly intermittent).
