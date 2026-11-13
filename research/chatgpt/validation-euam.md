# Validation of ChatGPT's euam.md ranked shortlist — 2026-11-07

Every check used the repo client (`world_legal_mcp._http`: real UA `Fontes/<ver> (+https://github.com/ykarapazar/fontes)`,
OS trust store). A handful of requests per site, ~1 s apart. No sign-ups, no logins, no bot checks bypassed.
No bot-challenge pages (Incapsula/Cloudflare/captcha) or TLS errors on any of the 10 sources.
"No terms found" means I looked and found none. It is not permission.

---

## 1. be — Vlaamse Codex (Flemish legislation) — **GO-WITH-CAVEAT**

- **Reachable:** yes. `codex.opendata.api.vlaanderen.be` returns JSON 200, no key.
- **Search:** `GET /api/WetgevingDocument/Zoeken?zoekTerm=wonen&take=1` → 200, `{"GevondenDocumenten":2506,"GevondenArtikelen":5715,"ResultatenLijst":[{"Id":1042457,...}]}`. Swagger (`/swagger/docs/v1`) also lists `GeavanceerdZoeken`, `Datum/{jaar}`, `numac/{numac}`, `Structuur`, `Versies`.
- **Document:** `GET /api/v2/WetgevingDocument/1030009/VolledigDocument` → 200, 1.46 MB JSON (Bestuursdecreet, 7 Dec 2018, Numac 2018032457). Article: `GET /api/WetgevingArtikelVersie/1357215` → `"Tekst":"Dit decreet regelt een gemeenschaps- en gewestaangelegenheid."` Structured JSON text, no PDF.
- **Terms/robots:** Swagger `info`: `"termsOfService":"Some terms"`, `"license":{"name":"Release notes",...}`. That is placeholder text, not a licence. I found no reuse terms on Algemeen.aspx, FAQ.aspx or apireleasenotes.aspx. Algemeen.aspx (https://codex.vlaanderen.be/Algemeen.aspx): "De Vlaamse Codex vormt geen officiële bekendmaking in de zin van de Grondwet." (the Codex is not an official publication). API host robots.txt: **404**. Website robots.txt only disallows DNN admin folders (`/admin/`, `/Portals/`, `/Resources/Search/`…). The adapter would use only the API host. No AI or automation clause found.
- **Coverage:** consolidated Flemish regulations "vanaf 1 januari 1959 tot vandaag" (homepage). Flemish region and community only. No federal law.
- **ChatGPT errors:** none found.

## 2. lc — Attorney General's Chambers, Revised Laws of Saint Lucia — **GO-WITH-CAVEAT**

- **Reachable:** yes, 200 (Sitefinity/Webflow site on `www.`).
- **Search (verified, ChatGPT had not checked it):** the page JS sends `window.location.href = "/laws-of-saint-lucia/search?query=" + text`. `GET https://www.attorneygeneralchambers.com/laws-of-saint-lucia/search?query=arbitration` → 200, 20 hits per page, relative links such as `arbitration-act/section-3`, paging `&p=2`. Index: `/laws-of-saint-lucia?by_letter=a`, `?p=N`.
- **Document:** HTML per section. `/laws-of-saint-lucia/arbitration-act/section-3`: "An arbitration agreement, unless a contrary intention is expressed therein, shall be irrevocable except by leave of the Court…"
- **Terms/robots:** `www…/robots.txt` redirects to `attorneygeneralchambers.com/robots.txt`, which only has `Disallow: /wp-admin/` (`/laws-of-saint-lucia/` is allowed). The only terms text is the footer "© 2026 Attorney General's Chambers". `/terms-of-use` → 404. No AI or automation clause.
- **Coverage:** "Revised Laws of Saint Lucia (2023)". Acts A–Z, about 8 index pages. Whether later amendments are included is **UNVERIFIED**.
- **ChatGPT errors:** none. It said search was unverified; it does work.

## 3. mk — Constitutional Court (ustavensud.mk) — **GO-WITH-CAVEAT**

- **Reachable:** yes, WordPress, 200.
- **Search (verified via WP REST):** `GET https://ustavensud.mk/wp-json/wp/v2/posts?search=имот&categories=80&per_page=3&_fields=id,date,link,title` → 200 JSON (`У.бр.32/2025`, …). Without a category filter, search also returns agendas and press posts, so the adapter must filter by category. Categories (`/wp-json/wp/v2/categories`): Одлуки (decisions) id 80 = **1481**, Решенија (resolutions) id 35 = **6408**, Издвоени мислења (separate opinions) 255. English "Decisions" 63, "Resolutions" 30. Albanian categories also exist.
- **Document:** full HTML text. U.No.251/2024: "Article 110 Indent 2 of the Constitution provides that the Constitutional Court … shall decide on the conformity of other regulations…". The oldest decision post is У.бр.60/1991 (11 Dec 1991), also full HTML: "Уставниот суд на Република Македонија, врз основа на членовите 110 и 112 од Уставот…".
- **Terms/robots:** robots.txt is `Disallow: /wp-admin/` only, so `/wp-json/` and posts are allowed. The footer has an IMPRESSUM link to `#` (empty) and "© 2026". No terms found.
- **Coverage:** constitutional decisions and resolutions, 1991–2026, mostly Macedonian. English for a subset only.
- **ChatGPT errors:** none. It understated coverage ("historical completeness unknown"; the archive goes back to 1991) and missed the WP REST API.

## 4. fr — Conseil d'État ArianeWeb — **GO**

- **Reachable:** yes, 200, no challenge.
- **Search (verified, ChatGPT had not checked it):** the ArianeWeb SPA (`/arianeweb/scripts/app-*.js`) POSTs form data to Sinequa. `POST https://www.conseil-etat.fr/xsearch?type=json`, `Content-Type: application/x-www-form-urlencoded`, body `advanced=1&type=json&SourceStr4=AW_DCE&text.add=laïcité&synonyms=true&scmode=smart&SkipCount=3&SkipFrom=0&sort=SourceDateTime1.desc,SourceStr5.desc` → 200 JSON, `DocumentCount` 115. Each hit has `SourceStr5` (number 499886), `SourceDateTime1` (2026-07-27) and `SourceStr39` (`/CE/decision/`), which map to `/fr/arianeweb/CE/decision/{date}/{number}`. Source codes: AW_DCE (CE decisions), AW_DCA (CAA), AW_DTC (Tribunal des conflits), AW_AJCE/AW_AJCA/AW_AJTC (analyses), AW_CRP (rapporteur public conclusions). The endpoint is undocumented and internal, so it may change without notice.
- **Document:** HTML. CE 506563 (21 Sep 2026): "1. La loi du 18 décembre 2023 pour le plein emploi a modifié l'article L. 5411-1 du code de travail…"
- **Terms/robots:** https://www.conseil-etat.fr/bas-de-page/mentions-legales: "les contenus présents sur ce site sont des informations publiques librement réutilisables" (conditions: integrity, date, and the source credit "Source : site internet du Conseil d'État"). No clause on robots, scraping, automation or AI. robots.txt: **404**.
- **Coverage:** the search page says "près de 300 000 décisions, analyses de jurisprudence et conclusions". It holds "les décisions de justice **importantes** du Conseil d'État … les décisions importantes des cours administratives d'appel", which is a selection, not every decision. Administrative courts only.
- **ChatGPT errors:** 1. "broad modern coverage" overstates it: the publisher says the collection is *important* decisions (a selection).

## 5. be — Constitutional Court (const-court.be) — **GO-WITH-CAVEAT**

- **Reachable:** yes, 200 (Nuxt SSR).
- **Search:** `/api/` is `Disallow`ed in robots, so I did **not** call it. A robots-allowed route exists instead: the sitemap (`/sitemap-archive.xml`) lists `/judgments?year=1985` … `?year=2026` (42 years). `GET /judgments?year=2025` → 200, with all of that year's judgments embedded in the Nuxt payload: description, verdict, keywords, `"3/2025"`, `"/public/f/2025/2025-003f.pdf"`. There are 177 judgments for 2025. Search = filter the year listing locally by keyword or number. No full-text search without the API.
- **Document:** text-layer PDF. `/public/f/2025/2025-100f.pdf`: "ECLI:BE:GHCC:2025:ARR.100 Cour constitutionnelle Arrêt n° 100/2025 du 26 juin 2025". `/public/f/1997/1997-059f.pdf` also has text ("Arrêt n° 59/97 du 14 octobre 1997").
- **Terms/robots:** https://fr.const-court.be/footer/disclaimer: "La reproduction des informations et des textes de ce site est autorisée moyennant la mention de la source ( www.const-court.be )." https://fr.const-court.be/apis: "la Cour a décidé de ne pas fournir de facilités spécifiques pour l'accès automatisé aux données" and "Le téléchargement massif de données est interdit." robots.txt: `Allow: /public/f/`, `Disallow: /public/`, `Disallow: /api/`, `Disallow: /*?*term=*`. `/judgments?year=` is not disallowed.
- **Coverage:** 1985–2026, about 177 judgments a year recently. French texts verified. NL/DE/EN **UNVERIFIED**.
- **ChatGPT errors:** none. Its API/robots conflict note is right. It missed the robots-safe year listing.

## 6. gy — CCJ appellate judgments — **GO (already built: `ccj` adapter)**

- **Reachable:** yes. `ccj.org/robots.txt` is `User-agent: *` / `Disallow:` (empty, so everything is allowed).
- **Search:** the existing repo adapter `src/world_legal_mcp/jurisdictions/ccj.py` (Ninja Tables JSON via admin-ajax) already finds it: `search_caselaw('Hassan')` → `[2026] CCJ 16 (AJ)`, "JANET HASSAN v ROMANIE GOUVEIA", 2026-11-03, with the PDF URL. `gy.py` already points users to `ccj`.
- **Document:** text-layer PDF, `/wp-content/uploads/2026/11/2026_CCJ_16_AJ_GY.pdf`: "[2026] CCJ 16 (AJ) GY IN THE CARIBBEAN COURT OF JUSTICE APPELLATE JURISDICTION ON APPEAL FROM THE COURT OF APPEAL OF THE CO-OPERATIVE REPUBLIC OF GUYANA".
- **Terms:** `/terms-of-use/` → 200, but the page has no terms text (consistent with the README entry). Footer © CCJ.
- **Coverage:** every CCJ judgment, 2005 on (per the adapter). Final appeals only, no lower Guyanese courts.
- **ChatGPT errors:** 1. It lists this as a "next adapter", but it is already implemented and live in the repo (`ccj`).

## 7. me — Službeni list Crne Gore — **NO**

- **Reachable:** yes, 200, no challenge.
- **Search:** `GET https://www.sluzbenilist.me/propisi?type=0&act=1&legislator=0&q=zakon%20o%20radu` → 200, with result links `/propisi/349283` (Zakon o radu), `/propisi/312153`, …. This is the parameter the page's Alpine.js sends as `q`.
- **Document:** **no text.** ChatGPT's "verified" URL `/propisi/dcf509f7-4e4d-45e3-896b-75fd8ebbefca/download` → **404** with our client. Record pages (`/propisi/349283`, `/propisi/337792`) show HTML metadata only ("Zakon o radu … Službeni list Republike Crne Gore, broj 43/2003 … Status: Nevažeći"). The body is one inline `data:image/jpeg` page per `?page=N`. There is no download or PDF link on either page. This matches the repo's own finding in `me.py` ("acts are shown only as page images (JPEG), no text without OCR").
- **Terms/robots:** https://www.sluzbenilist.me/robots.txt: `Content-Signal: search=yes,ai-train=no,use=reference`, `Allow: /`. Named AI crawlers (ClaudeBot, GPTBot…) get `Disallow: /`. Our UA is not named. No terms page found. Consolidated texts (REGIS) are paid, and per `me.py` their terms forbid copying.
- **Coverage:** gazette acts with metadata (98+ list pages for laws). Enacted text, not consolidated.
- **ChatGPT errors:** 1. The claimed free text PDF ("six pages of text", download pattern `/propisi/{uuid}/download`) does not reproduce: the URL is 404 and the site serves page images only.

## 8. mk — Ministry of Justice LDBIS — **GO-WITH-CAVEAT**

- **Reachable:** yes, 200 (ASP.NET WebForms + Telerik).
- **Search (verified):** two requests. `GET /` to read `__VIEWSTATE`/`__VIEWSTATEGENERATOR`/`__EVENTVALIDATION`, then `POST /` with those fields plus `Header$txtPrebaraj=правда за децата&Header$btnPrebaraj=Најди` → 200 at `/Prebaruvanje.aspx`, with a grid "66392 Закон за правда за децата … Службен весник на РСМ 66/2024 … 69731 Исправка на Законот…". The IDs map to `/PregledNaZakon.aspx?id={id}`.
- **Document:** text-layer PDF. ChatGPT's PDF URL `/PdfFiles/xgycdlx35rnu2v0hw0zlcytf.pdf` is now **404**: the token is regenerated on each record view. A fresh record fetch gave `/PdfFiles/u12db4c1ucjiaab4aqx0ddyy.pdf` → 200, 60 pages: "СОБРАНИЕ НА РЕПУБЛИКА СЕВЕРНА МАКЕДОНИЈА Врз основа на членот 75…". The adapter must fetch the record page, then the PDF, in the same session. Record pages list amendment chains (148/2013 → 152/2019 → 275/2019 → 66/2024 → 55/2025). The menu has a "Консолидирани" (consolidated) section, not tested.
- **Terms/robots:** robots.txt **404**. Footer: "Copyright © 2016 Ministry of Justice of the Republic of North Macedonia". No terms page found.
- **Coverage:** laws plus by-laws and other acts. The homepage lists the newest laws (ids around 75,320). Total count and earliest year **UNVERIFIED**.
- **ChatGPT errors:** none. It flagged the PDF URL lifetime itself, and that is confirmed: the URL expires.

## 9. ag — laws.gov.ag (Ministry of Legal Affairs) — **GO-WITH-CAVEAT**

- **Reachable:** yes, WordPress, 200.
- **Search:** there is no site-native search. The search form posts to a third-party service (`action="http://www.sitelevel.com/query"`, `crid=7x1jqeru`), which I did not use. WP REST has no custom law type (`/wp-json/wp/v2/types` shows only post/page/attachment…). The workable route: `GET /laws/alphabetical/?letter=E` → 74 rows of title, year and PDF link (`href='…/cap-143A.pdf'`), then filter locally. Annual and caps indexes also exist.
- **Document:** text-layer PDFs. Cap. 142: "CHAPTER 142 THE EASTERN CARIBBEAN CENTRAL BANK ACT Arrangement of Sections". Act No. 23 of 2017: "[Published in the Official Gazette Vol. XXXVII No. 57 dated 20th July, 2017]".
- **Terms/robots:** robots.txt is `Disallow: /wp-admin/` only. Homepage: "All legislation within the current year and will only be available at the Government Printery." Footer "©2026 - laws.gov.ag". No reuse terms found.
- **Coverage:** revised Caps plus annual Acts, bills and SIs. The site says the 2021 update project put "all of the laws passed" online, except the current year. Caps are revised editions, so they may not include later amendments (**UNVERIFIED**).
- **ChatGPT errors:** none found. It did not mention that site search is third-party, but it said search was "unresolved".

## 10. ch — entscheidsuche.ch — **GO-WITH-CAVEAT** (open question: non-official)

- **Reachable:** yes, 200.
- **Search:** `POST https://entscheidsuche.ch/_search.php` with an ES JSON body `{"query":{"bool":{"must":{"simple_query_string":{"query":"Mietzinsherabsetzung","default_operator":"and"}},"filter":{"term":{"hierarchy":"CH_BGer"}}}},"size":1,...}` → 200, 71 BGer hits. `{"query":{"term":{"hierarchy":"CH_BGer"}},"track_total_hits":true}` → **179,450** BGer documents, the oldest dated 1996-01-19.
- **Document:** HTML, `/docs/CH_BGer/CH_BGer_004_4C-319-2005_2006-02-08.html`: "4C.319/2005 /sza Urteil vom 8. Februar 2006 I. Zivilabteilung Besetzung Bundesrichter Corboz, Präsident…"
- **Terms/robots:** robots.txt: `Allow: /`, `Disallow: /hidden`, `Disallow: /archiv`, so `/_search.php` and `/docs/` are allowed. The publisher's README (github.com/entscheidsuche/entscheidsuche-mcp) says: "Die strukturierten Aufbereitungen des Vereins entscheidsuche.ch sind frei nutzbar" and "Offen — keine Authentifizierung, kein API-Key, lizenzfrei".
- **Caveat:** it is a non-profit aggregator, not an official source. The README rule is "official or public-body sources only", so using it is an open question. It is also not new: `research/eu_dach_fr_benelux.md` already documented it on 2026-11-05.
- **Coverage:** federal courts plus 26 cantons, DE/FR/IT. BGer from 1996 (179k documents).
- **ChatGPT errors:** none factual. It presents this as a fresh find, but the repo already had it.

---

## Summary

| Source | Verdict | One-line reason |
|---|---|---|
| be Vlaamse Codex | GO-WITH-CAVEAT | Open JSON API: search, full document and article text all work, no key. Licence field is a placeholder ("Some terms"). Not an official publication. |
| lc AG Revised Laws | GO-WITH-CAVEAT | Clean HTML per section plus a working `search?query=` route. No terms found. Currency after 2023 unverified. |
| mk Constitutional Court | GO-WITH-CAVEAT | WP REST search by category (1,481 decisions, 6,408 resolutions, 1991–2026) with full HTML text. No terms found. |
| fr ArianeWeb | GO | Explicit free-reuse terms, robots 404, full HTML, and the Sinequa `/xsearch?type=json` search works (undocumented). Selected "important" decisions only. |
| be Constitutional Court | GO-WITH-CAVEAT | Attribution reuse and text PDFs work. `/api/` is robots-disallowed and bulk download is banned, so use the `?year=` listings (local filter, no full text). |
| gy CCJ appellate | GO (already built) | The `ccj` adapter already serves it, verified live ([2026] CCJ 16 (AJ)). Nothing to build. |
| me Službeni list | NO | Acts are only JPEG page images. ChatGPT's "text PDF" URL is 404. Consolidated text is paid. |
| mk LDBIS | GO-WITH-CAVEAT | WebForms postback search works, and text PDFs work via per-view tokens (old URLs expire). No terms, robots 404. |
| ag laws.gov.ag | GO-WITH-CAVEAT | Text PDFs via A–Z/annual indexes (filter locally). Site search is third-party. Current year withheld. No terms. |
| ch entscheidsuche.ch | GO-WITH-CAVEAT | Technically best (ES search, 179k BGer documents, "frei nutzbar"), but non-official, which conflicts with the README rule. Open question. |

**ChatGPT errors found: 3**
1. me: claimed a verified free text-PDF download. The URL is 404 and the site serves page images only.
2. fr: "broad modern coverage" is overstated. ArianeWeb holds selected "important" decisions.
3. gy: listed as a next adapter, but the `ccj` adapter already covers it.

Not counted as errors: LDBIS PDF URL expiry (ChatGPT flagged it itself); ChatGPT not finding the search routes for lc, mk CC, fr and me (now verified above); entscheidsuche being a repeat of the repo's own 2026-11-05 research.
