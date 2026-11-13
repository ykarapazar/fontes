# Validation of ChatGPT's Africa shortlist (research/chatgpt/africa.md)

Checked 2026-11-07 from a UK connection with the repo's own client (`world_legal_mcp._http.get_client()`,
UA `Fontes/0.1.0 (+https://github.com/ykarapazar/fontes)`, OS trust store). No sign-up, no login, no
header changes. A handful of requests per site, at least 1.2 s apart (10 s on manshurat.org, which asks for `Crawl-delay: 10`).
PDF checks were done with `pdftotext`, `pdffonts` and `pdfinfo`.

Verdicts: GO = ready for an adapter; GO-WITH-CAVEAT = buildable, with a stated limit; NEEDS-PERMISSION;
NO.

---

## 1. Botswana e-Laws (legislation): **NO** (subscription paywall)

- **Reachable:** yes. `https://e-laws.botswanalaws.com/` returned 200 with no challenge.
- **Document text: PAYWALLED.** Only the Constitution is free:
  `/constitution-of-botswana/constitution-of-botswana/` gives full HTML ("30. Office of President There shall be a
  President of the Republic of Botswana who shall be the Head of State."). Every other category I opened
  shows the long title or table of contents, followed by:
  > "Members-only content Continue reading this exclusive content by subscribing to one of our membership plans. Subscribe Now Already a Member? Log In"

  I saw this on `/principal-legislation/waterworks/`, `/subsidiary-legislation/accountants-subsidiary-legislation/`,
  `/bulletin-2024/si-167-2024-…`, `/act-bulletin-2025/act-14-of-2025-…`, `/repealed-acts/botswana-college-of-distance-and-open-learning-repealed/`
  and `/historical-legislation/2024act/`.
- **Search:** the server-side `/?s=companies` returns an empty template ("No results were found"). Results are
  drawn in the browser by Algolia InstantSearch, using a search-only key embedded in the page's JS (app id `ZLF8VAG4QA`).
  I did not call it: the project's precedent (BOPA, bo TSJ) is not to use keys lifted from public JS. A list route
  does exist: the WordPress sitemaps (`/wp-sitemap-posts-post-1.xml`, `-2.xml`) list about 2,519 posts (360 principal, 196 subsidiary,
  181 historical, plus bulletins 2015–2025). That does not help, because the texts are gated.
- **Terms** (`/privacy-policy/`): users must not "Disrupt website operations"; "All content on this website, including
  text, logos, and images, is the property of the Government of Botswana". No automation ban.
- **Robots** (`/robots.txt`): only `# Algolia-Crawler-Verif`, `Allow: /blog-news/*` and a Sitemap line. There is no
  User-agent group and no Disallow.
- **Coverage:** consolidated principal and subsidiary legislation, bulletins 2015–2025, repealed and historical acts.
  The "from 1890" claim is UNVERIFIED.
- **ChatGPT errors:**
  1. "Full HTML verified; no login": wrong. Full text is free only for the Constitution; everything else sits behind a subscription or login.
  2. "a search field": overstated. Search runs client-side through Algolia with a key in the page JS, and server-side `?s=` returns nothing.

## 2. Angola Tribunal Constitucional (case law): **GO-WITH-CAVEAT**

- **Reachable:** yes, 200, no challenge. `robots.txt` returns **404** (no rules).
- **Search works** (POST, multipart, the same request the page's form sends):
  `POST https://www.tribunalconstitucional.ao/?altTemplate=apijudgmentslist` with fields
  `FastSearchType, AccNumber, AccYear, ProcessNumber, ProcessYear, QueryAdd, Species, accReporter, Date`.
  Example: `AccYear=2025, QueryAdd=eleitoral` returned an HTML fragment with 14 links such as `/pt/acordaos/acórdão-nº-1001-2025/`.
  An advanced search exists at `/?altTemplate=advancedSearch`, adding `startRange/endRange/QueryRemove/accFormation`.
- **Document text:** HTML. `/pt/acordaos/acórdão-n-º-1161-2026/` begins "ACÓRDÃO N.º 1161/2026 PROCESSO N.º 1420-D/2025 …
  Em nome do Povo, acordam, em Conferência, no Plenário do Tribunal Constitucional". Older decisions are PDFs
  under `/media/{id}/{name}.pdf`. `001.pdf` (Acórdão 001/2008) has a text layer, apparently OCR ("Processo n. 000l1PPC/08").
- **Coverage:** the archive at `/pt/jurisprudencia/arquivo/` lists the years 2008–2026 and 1,082 PDF links. The latest is
  Acórdão 1161/2026. The court handles constitutional matters, party and electoral disputes and similar cases.
- **Terms:** none found. There are no terms, privacy or legal-notice links on the home page or the listing.
- **Caveat:** no terms at all, and search needs a multipart POST to a template endpoint.
- **ChatGPT errors:** none found. Its "earliest year unknown" can now be answered: 2008.

## 3. Djibouti Journal officiel électronique (legislation): **GO-WITH-CAVEAT**

- **Reachable:** yes, 200, no challenge.
- **Robots:** `User-agent: *` / `Disallow: /wp-admin/` / `Disallow: /wp-content/uploads/wpo/wpo-plugins-tables-list.json`.
  Neither public text routes nor `/wp-json/` are excluded.
- **Search:** the site's `/?s=code+du+travail` returned **no** `texte-juridique` results. The WordPress REST API does work:
  `GET /wp-json/wp/v2/texte-juridique?search=code du travail&per_page=5&_fields=id,date,link,title,content`
  returned 200 with `X-WP-Total: 656` and full HTML bodies in `content.rendered` (2k–56k characters). Ranking is loose: the top hits were budget laws.
  Date filtering works too: `before=2000-01-01&after=1990-01-01` gave 1,567 texts.
- **Document text:** HTML. "ARRÊTE Article 1 : Est approuvé et rendu exécutoire : 1. Le budget prévisionnel de fonctionnement,
  exercice 2026…". 1999 arrêtés also come back with full text.
- **Coverage:** `X-WP-Total` reports **58,223** `texte-juridique` items. The oldest record is dated "1392-11-17", which is bad
  metadata. There are real texts from the 1990s through November 2026, with taxonomies `institution` and `nature-dun-texte`.
- **Terms:** the footer says "Tous droits réservés." The page sitemap has no legal-notice page. It does have
  `/se-connecter/`, `/sinscrire/votre-abonnement/` and `/mettre-a-jour-votre-carte-bancaire/`, so some paid tier exists,
  but I did not establish what it gates. Individual texts were open.
- **Caveat:** "all rights reserved" with no reuse terms; a subscription tier of unknown scope; weak keyword ranking.
- **ChatGPT errors:** none found. It wrote "API unverified"; there is a working WP REST API.

## 4. South Africa Constitutional Court (case law): **GO-WITH-CAVEAT**

- **Reachable:** yes, 200, no challenge, on both `collections.concourt.org.za` (DSpace 7) and `www.concourt.org.za` (Joomla).
- **Document text:** the PDF has a text layer. `/bitstreams/77cfb38f-…/download` redirects to `/server/api/core/bitstreams/{uuid}/content`
  (36 pages): "CONSTITUTIONAL COURT OF SOUTH AFRICA Case CCT 246/25 In the matter between: FUSI SIMON MOFOKENG".
  Item metadata comes as JSON from `/server/api/core/items/{uuid}`, with fields `dc.title`, `dc.identifier.citation` ("[2026] ZACC 43"),
  `dc.date.judgment`, `dc.contributor.judge`, `dc.concourt.synopsis` and `dc.link.judgment`.
- **Search: repository search is robots-disallowed.** The DSpace REST search (`/server/api/discover/search/objects`)
  matches `Disallow: /*/discover` and `Disallow: /*/search`, and `/browse/*` is also disallowed. Two routes remain:
  (a) the main site's Joomla search, `https://www.concourt.org.za/index.php/component/finder/search?q=pardon`, which
  returned the Mofokeng judgment page and is not disallowed (main robots only blocks `/components/`, `/api/` and similar);
  and (b) `/index.php/decisions-and-case-flow/recent-judgments` plus its RSS feed. Both cover **recent judgments only**.
  For older material the only allowed route is fetch-by-UUID, with UUIDs taken from `sitemap0.xml` (no titles).
- **Robots:** quoted above. Named downloader bans (HTTrack, WebCopier, "Fetch", "libwww" and others) do not match our UA.
- **Terms:** none located. The main-site footer reads "Copyright © Constitutional Court of South Africa All Rights Reserved".
- **Coverage:** `sitemap0.xml` lists 28,975 `/items/` (all item types, not only judgments). The earliest judgment year is UNVERIFIED.
- **Caveat:** no allowed full-history search; terms not located.
- **ChatGPT errors:** none found.

## 5. Liberia Judiciary (legislation + case law): **GO-WITH-CAVEAT (case law); legislation not worth an adapter**

- **Reachable:** yes, 200, no challenge. **Robots:** `User-agent: *` / `Disallow: /wp-admin/` / `Allow: /wp-admin/admin-ajax.php`.
- **Search works** through the WP REST API: `GET https://judiciary.gov.lr/wp-json/wp/v2/posts?search=Norman&per_page=5&_fields=date,link,title`
  returned 2 hits, including "Prince Desmond Norman vs Republic of Liberia (08/27/2026)".
- **Case-law text:** each opinion post is an HTML **stub** linking a PDF, for example `/wp-content/uploads/2026/10/Prince-Desmond-Norman-v.-R.L.pdf`
  (13 pages, made in Word, with a text layer): "IN THE HONORABLE SUPREME COURT OF THE REPUBLIC OF LIBERIA SITTING IN ITS MARCH TERM, A.D. 2026".
- **Legislation text:** `/judiciary-law/` is a list of 4 links. "NEW JUDICIARY LAW" leads to an HTML stub, which links
  `/wp-content/uploads/2022/12/NEW-JUDICIARY-LAW.pdf` (91 pages, Word, text layer: "JUDICIARY LAW … TITLE 17 … Approved May 10, 1972").
  The other three are Criminal Court D, Criminal Court E and the Judiciary Financial Act, all PDFs. That is about 5 documents in total.
- **Coverage:** Supreme Court opinions on-site from 2016 (`/opinions-listing/`) to 2026; the 2026 page lists dozens of 2026 opinions.
  1862–1915+ links go to LiberLII, a different host that I did not check.
- **Terms:** only a privacy policy. No reproduction or automation clause found.
- **ChatGPT errors:**
  3. "Official HTML Judiciary Law verified / VERIFIED—text, English HTML": wrong. The HTML page is a link stub, and the law is a 91-page PDF.

## 6. Guinea-Bissau Assembleia Nacional Popular (legislation): **GO-WITH-CAVEAT (very low value)**

- **Reachable:** yes, 200, no challenge. **Robots:** `User-agent: *` / `Disallow:` (Googlebot-only form exclusions).
- **Search works:** `https://www.parlamento.gw/@@search?SearchableText=eleitoral` (Plone) returned results including
  `/leis/legislacao/lei-do-recenseamento-eleitoral` and `/leis/legislacao/lei-da-observacao-internacional-eleitoral`.
  An RSS variant is at `/search_rss?SearchableText=…`.
- **Document text:** HTML. "ARTIGO 1.º A Guiné-Bissau é uma República soberana, democrática, laica e unitária." Lei da Cidadania
  (Lei n.º 2/92) is also full HTML, marked "última modificação 06/04/2015".
- **Coverage:** tiny. `/leis/legislacao` has 4 laws (citizenship, international election observation, voter registration,
  party framework), plus the Constitution, 2 statutes/regimento, about 5 treaty pages and an empty `leis-federais`.
  `legislacao-municipal` returns 404. Nothing updated since about 2015.
- **Terms:** none located.
- **ChatGPT errors:** none found. Its "no search query verified" can now be answered: Plone `@@search` works.

## 7. Egypt Manshurat (legislation): **GO-WITH-CAVEAT**

- **Reachable:** yes, 200, no challenge, no login on the pages I opened.
- **Operator:** a project of the **Law and Society Research Unit, American University in Cairo** (about page `/node/21612`).
- **Terms** (`https://manshurat.org/node/21612`): "Copyright is held by the author(s) unless otherwise stated. Requests for permission
  to quote or use any content should be addressed to the author(s) directly." The Arabic version scopes this to materials that contain opinions.
  There is no automation ban.
- **Robots:** `Crawl-delay: 10`, `Disallow: /search/` and `/?q=search/`. The site's own search form is `GET /search?keys=…`
  (no slash after `search`), which the literal rule does not match. The intent is ambiguous.
- **Search works:** `https://manshurat.org/search?keys=قانون العمل` returned 28 document links (e.g. `/node/23344` "إصدار قانون العمل").
  It is better to treat it as disallowed-in-spirit and ask, or to accept it with the 10 s delay. Open question.
- **Document text: mixed.** `/content/qnwn-lml-ljdyd-2025` (Labour Law 2025) is full HTML: "مادة (1) : يقصد فى تطبيق أحكام هذا القانون…".
  `/node/14677` (Penal Code) is HTML but stamped "آخر تعديل: 15 أغسطس 2021". `/node/23344` (Labour Law 137/1981) has **no HTML text**,
  only a download (`/file/33796/download?token=…`). That download is a **scanned 54-page image PDF** (no fonts; producer pdfimage.com).
- **Coverage:** laws, regulations, decrees, constitutions, preparatory works, court rulings and NGO reports. Node ids go up to about 74,800
  (all document types). The legislation count is UNVERIFIED.
- **ChatGPT errors:**
  4. "Large readable Arabic law pages": overstated. Some laws are scanned PDFs only, and some HTML is stale (Penal Code to 2021).
  5. "Substantive reuse terms not located": wrong. The about page has a copyright and permission clause and names AUC as the operator.
  6. "search route excluded": imprecise. Robots excludes `/search/`; the live form uses `/search?keys=`, which is not literally excluded.

## 8. Nigeria PLAC Laws of Nigeria (legislation): **GO-WITH-CAVEAT**

- **Reachable:** yes, 200, no challenge. `robots.txt` → **404**.
- **Search: BROKEN at source.** `searchlaw.php?search=` returned an empty list for `Companies`, `COMPANIES` and the site's own
  placeholder example, `Administration`. The replacement is the title list: `index.php?page=1..69`, with 8 titles per page and 2 on page 69, about 546 acts.
  It could be fetched once and cached; that is 69 requests.
- **Document text:** HTML. `view2.php?sn=14`: "Short title, etc. (1) This Act may be cited as the Acts Authentication Act." `sn=200`
  (Import (Prohibition) Act) is also HTML.
- **Coverage:** the FAQ states it holds "statutes of the Federation of Nigeria as at 31 December 2002" and that "LFN 2004 has not been revised
  or updated". Later acts are said to be at `placng.org/i/acts/`, which I did not check.
- **Terms:** footer "© Copyright Policy and Legal Advocacy Centre 2026". No terms page found.
- **Caveat:** the content stops at 2002, and search has to be rebuilt from the title list.
- **ChatGPT errors:** none outright. It did not notice that the search form returns nothing.

---

## Spot checks of ChatGPT's "ruled out" claims

**Kenya Law terms: CONFIRMED, quote exact.** `https://kenyalaw.org/terms-of-use/`:
> "Scraping, deployment of unauthorized bots and bulk downloading from this website is strictly prohibited."

ChatGPT missed a stronger clause in §9: "Automated data scraping, bulk extraction, commercial redistribution, or training of
machine learning/AI models without an explicit Licensing Agreement from NCLR is strictly prohibited." Robots has
`Content-Signal: ai-train=no, search=yes, ai-input=no` and disallows `/api/`, `/judgments/`, `/search/` and `/akn/ke/judgment/`. Ruling it out is correct.

**Guinea coursupreme.org.gn robots: CONFIRMED but mischaracterised.** `https://coursupreme.org.gn/robots.txt` gives
`Disallow: /` to about 70 named agents. These include GPTBot, ChatGPT-User, ClaudeBot and anthropic-ai, but also **Googlebot, bingbot,
DuckDuckBot, Applebot, archive.org_bot, curl, Wget** and uptime monitors. It ends with `User-agent: *` / `Allow: /`. This is a
block-every-known-bot list, not specifically an AI ban. Fontes is not named, so the literal rule allows us. The intent is plainly
"no bots", so ruling it out as an unrestricted source is reasonable. I do not count this as an error.

---

## Summary

| Source | Verdict | One-line reason |
|---|---|---|
| Botswana e-Laws (leg) | **NO** | Everything except the Constitution is "Members-only content" behind a subscription; search is client-side Algolia. |
| Angola Tribunal Constitucional (case law) | **GO-WITH-CAVEAT** | HTML judgments, OCR-text PDFs 2008–2026 (~1,160), POST search works; no terms, robots 404. |
| Djibouti eJO (leg) | **GO-WITH-CAVEAT** | WP REST API gives full HTML for ~58k texts with search/date filters; "Tous droits réservés", paid tier of unknown scope. |
| South Africa ConCourt (case law) | **GO-WITH-CAVEAT** | Text PDFs + JSON metadata by UUID; repository search robots-disallowed, main-site search/RSS covers recent judgments only. |
| Liberia Judiciary (case law; leg) | **GO-WITH-CAVEAT** (case law) | WP REST search + text-layer PDFs 2016–2026; "legislation" is ~5 PDFs, not HTML. |
| Guinea-Bissau parlamento.gw (leg) | **GO-WITH-CAVEAT** | Works (HTML + Plone search) but only ~10 documents, untouched since ~2015. |
| Egypt Manshurat (leg) | **GO-WITH-CAVEAT** | AUC project; author-copyright clause; Crawl-delay 10; search route ambiguous vs robots; some laws scanned-only. |
| Nigeria PLAC (leg) | **GO-WITH-CAVEAT** | Clean HTML, no robots; frozen at 31 Dec 2002 and search broken (use 69-page title list). |

**ChatGPT errors found: 6.** Botswana 2 (free full text/no login; search field), Liberia 1 (Judiciary Law as HTML), Egypt 3
(readable pages overstated, reuse terms "not located", search-route exclusion imprecise). The biggest one: its **#1-ranked
source (Botswana) is a subscription site**.
