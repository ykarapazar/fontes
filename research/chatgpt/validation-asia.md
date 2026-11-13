# Validation of ChatGPT's Asia/Pacific shortlist (research/chatgpt/asia.md)

**Checked on:** 2026-11-07, from a UK network.

**Client:** the repo's `world_legal_mcp._http`. It sent our real UA, `Fontes/<ver> (+https://github.com/ykarapazar/fontes)`, with no faked headers, spaced requests about 1.2 s apart, and made a handful of requests per site. No sign-ups and no logins.

**Status labels:**
- **UNVERIFIED** means I could not check the item; the reason is given each time.
- **Not legal advice.** Terms quotes are reproduced as found. Whether a court site's terms actually bind is not assessed.

---

## tw — law.moj.gov.tw (legislation) — **GO (already built)**

1. **Reachable:** yes. These all returned 200 with no challenge: `robots.txt`, `/LawClass/LawAll.aspx?pcode=B0000001` (718 KB HTML) and `/Copyright.aspx`.
2. **Search:**
   - robots disallows everything except three paths: `User-agent: *` / `Disallow: /` / `Allow: /News/NewsDetail.aspx` / `Allow: /LawClass/LawAll.aspx` / `Allow: /SearchEngineSitemap.aspx` (https://law.moj.gov.tw/robots.txt).
   - Search pages are therefore off-limits.
   - Replacement: `/SearchEngineSitemap.aspx` is allowed and lists 11,814 `LawAll.aspx?pcode=` URLs. They carry no titles, so a title index would need one fetch per law. A pcode lookup works today.
3. **Text:** HTML, e.g. "第 1 條 民事，法律所未規定者，依習慣；無習慣者，依法理。"
4. **Terms:**
   - The Copyright page (https://law.moj.gov.tw/Copyright.aspx) applies 政府資料開放授權條款-第1版: "使用者亦無須取得本機關之書面或其他方式授權；然使用時應註明出處。" Attribution is required.
   - Personal data must still follow the PDPA.
   - Copyright.aspx itself falls under `Disallow: /`. It was read once, by hand, as terms.
5. **Coverage:** the site shows "法規整編資料截止日 115/10/30", which is current.
6. **ChatGPT errors:**
   - It presents tw as a "next adapter", but `src/world_legal_mcp/jurisdictions/tw.py` already does MOJ legislation by pcode via LawAll.aspx, plus FJUD case law.
   - Its claims about the text, robots and licence are correct.

## vu — judiciary.gov.vu (judgments) — **GO-WITH-CAVEAT**

1. **Reachable:** yes, all 200, no challenge.
2. **Search:**
   - `GET /court-activity/judgments?filter_search=trespass` returned 197 results, which look full-text; Peau v Jack ranked first.
   - The jurisdiction filter `filter_juridiction` takes Civil, Court of Appeal, Island Court, Judgments, Magistrates Court or Supreme Court.
   - Paging uses `?start=` in steps of 200 rows.
   - **Caveat:** the Joomla filter is sticky per session cookie. A later unfiltered `?start=2800` still came back with "trespass" applied, so the adapter must set or clear filters explicitly on every request.
3. **Text:**
   - The judgment page `/court-activity/judgments/2912` has the full text in HTML: "The issue to be determined is whether there is trespass by the defendant."
   - The "Official PDF" (`/media/com_pgitjudgements/pdfs/2026-10-20-civil-case-227-of-2025-peau-v-jack-….pdf`, 4 pages) is a **scanned** TOSHIBA e-STUDIO image with no text layer. Use the HTML.
4. **Terms and robots:**
   - robots is the Joomla default. It disallows /administrator/, /api/, /bin/, /cache/, /cli/, /components/, /includes/, /installation/, /language/, /layouts/, /libraries/, /logs/, /modules/, /plugins/ and /tmp/. `/media/` is not listed.
   - Our paths, `/court-activity/judgments*` and `/media/com_pgitjudgements/pdfs/`, are allowed.
   - Footer: "© 2026 Government of Vanuatu. All rights reserved."
   - No terms page found, and no AI or automation clauses seen.
5. **Coverage:**
   - About 2,800–3,000 judgments; the last `start=2800` page exists. The exact count is UNVERIFIED.
   - The page heading says "Judgments since 2017", but the last page includes 2016 decisions, e.g. Aru v Joshua, heard 06 May 2016.
   - Courts: Supreme Court and Court of Appeal, with Island and Magistrates filters also offered.
6. **ChatGPT errors:**
   - "Full HTML plus PDF" implies a text PDF; the PDF is scanned.
   - "Index 2017–2026" is wrong: the index reaches into 2016.
   - "Search parameters not verified": they are a simple GET (minor).

## ir — ara.jri.ac.ir (case law) — **NEEDS-PERMISSION**

1. **Reachable:** yes. The home page and `/Judge/Text/41692` returned 200. `robots.txt` returned 404 (an HTML error page), so there are no robots rules.
2. **Search:**
   - `POST /Judge/Index` (form-encoded, no CSRF token) with fields `Title`, `IsTitleSearch=true`, `IsAbstractSearch`, `IsTextSearch`, `_IsOfficial/_IsCivil/_IsPenal`, `fromOverDate`, `toOverDate`, `CaseNo`, `SeachTextType=3`, `SortDesc=True`, `alertcript=`.
   - Example: Title "قتل عمدی" returned 3 pages of 25 results, including ids 43373 and 41692.
3. **Text:**
   - HTML, e.g. "عنوان: جنبه عمومی بزه قتل عمدی … رأی دادگاه".
   - Parties are reduced to initials, and the anonymisation is partial in places. Treat the content as potentially containing personal data.
4. **Terms:**
   - Footer: "کلیه حقوق برای پژوهشگاه قوه قضاییه محفوظ است" ("all rights reserved to the Judiciary Research Institute").
   - No terms page or licence found.
5. **Coverage:**
   - The home page shows 43,701 judgments, dated 1389/02/25–1405/05/31, with the last publication on 1405/07/29.
   - By court: first instance 13,642; provincial appeal 12,814; Administrative Justice Court 12,700; Supreme Court 7,225.
   - These numbers match ChatGPT's.
6. **Hosting facts:**
   - `ara.jri.ac.ir` is a CNAME for `frontier.cdn.ir`, which resolves to 193.151.157.x.
   - That range is in AS60077 "AT-CLOUD" (Asiatech), netname IR-AT-20210316, country IR, address Tehran.
   - The DNS nameservers are `sonic201/202.irandns.com`.
   - The operator is the Judiciary Research Institute, part of Iran's judiciary.
7. **ChatGPT errors:** none found in its row. The reasons for this verdict are the all-rights-reserved footer plus the Iran judiciary hosting.

## mn — legalinfo.mn (legislation) — **GO-WITH-CAVEAT**

1. **Reachable:**
   - Yes, now. `/` (which redirects to `/mn`) and the detail pages return 200. `robots.txt` returns 404.
   - SIGNUPS.md says the site was unreachable from the UK, but that is no longer true today.
2. **Search:**
   - The `GET /mn/search?sq=` HTML is empty because the results are rendered by JS.
   - The working route is `POST https://legalinfo.mn/mn/ajaxList/` with `title=Иргэний хууль&isvalid=1`. It returns JSON `{"Html","word"}` whose rows link to `detail?lawId=N`; this example gave 9 hits.
   - More parameters are visible in law.js (`filtercategorytypeid`, `filterstartdate`, …).
3. **Text:**
   - HTML. `/mn/detail?lawId=11954` gave full Mongolian text, a Constitutional Court decision about the Civil Code.
   - `/mn/detail/15789` is an English page: "Unofficial translation LAW ON CURRENCY REGULATION 12 May, 1994 … Article 1. Purpose of this law 1.1. …"
4. **Terms:**
   - Footer: "© 2025 legalinfo.mn Бүх эрх хуулиар хамгаалагдсан." ("all rights protected by law").
   - The system rules page (`/mn/about/16106883680221`) embeds a 12-page **scanned** PDF with no text layer, so it is UNREADABLE and its terms are UNVERIFIED.
   - The privacy policy mentions "enforcing our terms of service", but no terms page was found.
   - The site has login and captcha widgets, but neither is needed to read documents.
5. **Coverage counts on the site:**
   - 20,048 acts in total
   - 956 laws
   - 2,597 parliamentary resolutions
   - 5,800 government resolutions
   - 3,275 administrative acts
   - 333 Constitutional Court decisions
   - 259 Supreme Court resolutions
   - 702 treaties
   - 347 law translations
6. **ChatGPT errors:** it says the law page "includes an English translation", but id 15789 *is* the translation, a separate record (minor).

## ws — ag.gov.ws (consolidated legislation) — **GO-WITH-CAVEAT**

1. **Reachable:** yes. The consolidation page returned 200, and `robots.txt` returned 404.
2. **Search:**
   - There is no search, only a single A–Y page with 267 PDF links, all under `/wp-content/uploads/2024/02/`.
   - Workaround: list that one page and filter by title.
3. **Text:**
   - Text-layer PDF (Word 2013), e.g. a 12-page sample: "SAMOA ATTORNEY GENERAL'S OFFICE ACT 2013 … This Act has been revised by the Legislative Drafting Division in 2013 – 2023".
4. **Terms:** footer "© Copyright - 2026 | Office of the Attorney General". No terms or licence page found.
5. **Coverage:** the 2023 consolidation only. Acts after 2023 are not on this page.
6. **Caveat (security):**
   - The page HTML contains hidden SEO-spam links, e.g. `<style>.schg { position: absolute; left: -2551px; }</style><a href="https://76-unblocked-games.s3.amazonaws.com/index.html">unblocked games 66</a>`, plus sites.google.com "unblocked games" links.
   - This looks like a compromised WordPress site.
   - An adapter must whitelist `ag.gov.ws/wp-content/uploads/*.pdf` links only.
7. **ChatGPT errors:** none found. It did not mention the spam injection.

## bn — judiciary.gov.bn (judgments) — **NEEDS-PERMISSION**

1. **Reachable:** yes. The index and PDFs returned 200, and `robots.txt` returned 404.
2. **Search:**
   - WordPress `GET /?s=misrepresentation` works.
   - Post pages, e.g. `/civil-appeal-no-1-of-2026/`, link to PDFs under `/wp-content/uploads/YYYY/MM/`.
3. **Text:**
   - Text-layer PDF. OS 10/2026 has 6 pages: "… Respondent/Plaintiff Hj Jameel Ahmed Basheer Ahmed".
4. **Terms:**
   - The judiciary footer shows "Privacy Statement | Terms of Use | Disclaimer" as unlinked text, plus "Copyright Goverment of Brunei Darussalam. All Right Reserved."
   - The Government's Terms of Use at https://www.gov.bn/term-of-use/ say:
     - 2.2: "You may not reproduce, copy, distribute, store or in any other fashion re-use material from the Website unless otherwise indicated on the Website or unless given express written permission"
     - §4: "Deep linking (i.e. links to specific pages within the site) requires the express permission of the Government."
     - Prohibited use (e): "Reselling or providing a website, the contents and services or any part from the website to the person or entity for profit or otherwise."
   - These terms are written for www.gov.bn. Whether they bind judiciary.gov.bn is UNVERIFIED, but the judiciary footer refers to "Terms of Use" under the same Government copyright.
5. **Coverage:**
   - About 26 entries per page, with 41 pages; page 40 already reaches 2000–2006. That suggests roughly 1,000+ judgments (exact count UNVERIFIED).
   - Courts: Court of Appeal, High Court and Intermediate Court.
6. **ChatGPT errors:**
   - "Substantive terms not located" is wrong: the gov.bn terms restrict reproduction and deep linking.
   - "Older cases including 2017" understates the range, which goes back to 2000.

## pw — palaucourts.gov.pw — **GO-WITH-CAVEAT**

1. **Reachable:**
   - Yes. `/upload-1.cshtml` returned 200 (415 KB), and the 2026 Palau 3 PDF returned 200.
   - `robots.txt` returned 404 (HTML).
2. **Search:**
   - The page labels a "Decision Search Page", but the saved HTML has no search form fields and no link to a search page, so search is UNVERIFIED.
   - Workaround: the single index page lists 1,697 PDF links, which can be filtered by citation.
3. **Text:**
   - Text-layer PDF (PDFMaker for Word). 2026 Palau 3 has 7 pages: "IN THE SUPREME COURT OF THE REPUBLIC OF PALAU APPELLATE DIVISION PALAU NATIONAL COMMUNICATIONS CORPORATION, Appellant, v. WILLY WALLY".
   - Text in the ROP Reporter PDFs is UNVERIFIED (not sampled).
4. **Terms:**
   - The page says: "This database is provided as a public service." It asks users to check summaries against the documents and warns that some decisions were reversed.
   - No terms, licence or copyright clause found.
5. **Coverage:**
   - 327 neutral citations, 2016–2026: 30, 37, 28, 40, 32, 40, 28, 29, 34, 15 and 14 per year.
   - 1,359 ROP Reporter decisions, vols 1–23 (`/doc/ROP_Reporters/{n}ROP/{n} ROP {page}.pdf`).
   - Also digests and a citator.
   - Filenames are irregular (e.g. `2026 Palau 5_.pdf`, with spaces), so take the links from the index rather than building them.
6. **ChatGPT errors:**
   - "Index timed out" was not reproduced: it returned 200.
   - ChatGPT missed the 1,359 ROP Reporter decisions (an omission; not counted as an error).

## om — mjla.gov.om (laws) — **GO-WITH-CAVEAT**

1. **Reachable:** yes. `/laws/1` returned 200. robots.txt: `User-agent: *` / `Disallow: /search` / `Disallow: /statistics` / `Sitemap: https://mjla.gov.om/sitemap.xml` (https://mjla.gov.om/robots.txt).
2. **Search:**
   - `/search` is robots-disallowed.
   - Replacement: browse `/laws/1/page/{n}`, which gives about 27 laws per page across at least 9 pages (page 8 is the 1970s) and a 2014–2023 year selector. That is roughly 250 laws (UNVERIFIED).
3. **Text:**
   - **Trap:**
     - `download.php?file=Book377528.pdf` (ChatGPT's "verified" sample), `file=Book520118.pdf` and `file=nonexistent-xyz.pdf` all return the *identical* file: 140,291 bytes, md5 `fe055ea0e642aa67dd4375cdfbbd500f`, a 3-page "قانون مقاطعة إسرائيل قانون رقم 9 لسنة 1972".
     - The filename route returns this same default file for any name, including one that does not exist.
   - **Working route:**
     - `download.php?file=230` (the numeric id from `/laws/ar/1/show/230/`) gives the real 23-page Royal Decree 2026/61.
     - Its text layer has systematic glyph damage: "مر�ســوم �سلطانــي رقم ٢٠٢٦/٦١ ب�إ�صـدار قانـون مكافحـة جرائـم تقنيـة املعلومـات". Cleanup or OCR is needed.
   - The show page has no HTML law text, and its date field reads a bogus "01 يناير 1970".
4. **Terms:**
   - Footer: "محتويات هذا الموقع مرخصة بموجب الرخصة الحكومية المفتوحة - سلطنة عٌمان".
   - The licence PDF (https://www.mjla.gov.om/images/opendata/file/Book110050.pdf) grants: "استخدام وإعادة استخدام البيانات لأي غرض تجاري أو غير تجاري" and "نسخ، وتنزيل، ونشر، وتوزيع، ونقل، ومعالجة البيانات".
   - Attribution and disclosure of modifications are required, and the licence states it is compatible with CC 4.0.
   - Exclusions: personal data, logos, IP-protected material, ID documents and classified data.
5. **Coverage:** Royal Decree laws from the 1970s to 2026.
6. **ChatGPT errors:**
   - Its "verified" Book377528.pdf sample is the endpoint's fallback file, and the `file={filename}` route is unreliable; the numeric id is required.
   - It understates the text damage, which is systematic in recent laws, not an isolated quirk.

## au — hcourt.gov.au (High Court case law) — **NO (for now)**

1. **Reachable:** no. `robots.txt`, the judgments index and a judgment page all failed with `ReadTimeout`; robots.txt was retried once and timed out again. This matches the earlier note in `au.py` that the Akamai front of www.hcourt.gov.au resets requests from the UK.
2. **Search:** UNVERIFIED (unreachable).
3. **Text:** UNVERIFIED (unreachable).
4. **Terms and robots:** UNVERIFIED (unreachable).
5. **Coverage:** UNVERIFIED (unreachable).
6. **ChatGPT errors:** "VERIFIED — text PDF" could not be reproduced with our client. To ChatGPT's credit, it also reported robots as a timeout.
7. **Option:** re-test from a non-UK network before dropping this.

---

## Summary

| source | verdict | one-line reason |
|---|---|---|
| tw law.moj.gov.tw | GO (already built) | OGDL licence (attribution); robots allows only LawAll; tw.py already does this — not a new adapter |
| vu judiciary.gov.vu | GO-WITH-CAVEAT | Full HTML text, simple GET search; PDFs are scanned; sticky session filter; "all rights reserved", no terms |
| ir ara.jri.ac.ir | NEEDS-PERMISSION | Works technically (POST search, HTML, 43,701 judgments), but all rights reserved, no licence, and hosted by Iran's judiciary in Tehran (AS60077) |
| mn legalinfo.mn | GO-WITH-CAVEAT | Reachable again; ajaxList POST search and HTML text; terms PDF is scanned and unreadable, "all rights protected" |
| ws ag.gov.ws | GO-WITH-CAVEAT | 267 text PDFs, 2023 consolidation only, no search; site has injected spam links, so filter links |
| bn judiciary.gov.bn | NEEDS-PERMISSION | Text PDFs and WP search work, but gov.bn terms ban reproduction and deep linking without written permission |
| pw palaucourts.gov.pw | GO-WITH-CAVEAT | 1,697 text PDFs (327 neutral citations 2016–26, plus ROP vols 1–23) on one page; no terms found; search UNVERIFIED |
| om mjla.gov.om | GO-WITH-CAVEAT | Open Government Licence (commercial OK, attribution); filename download returns a fallback file, so use numeric ids; text layer glyph-damaged |
| au hcourt.gov.au | NO (for now) | ReadTimeout on every request from our client (Akamai); nothing verifiable |

**ChatGPT errors found: 11.**
1. tw is presented as a new adapter, but it already exists.
2. vu: the PDF is implied to have text, but it is scanned.
3. vu: the index range given as 2017–2026 actually includes 2016.
4. vu: search parameters were called unverified, but they are a plain GET.
5. mn: id 15789 is the translation itself, not a law page that includes one.
6. bn: "substantive terms not located" is wrong; they restrict reproduction and deep linking.
7. bn: the "2017" range understates coverage, which goes back to 2000.
8. om: the "verified" Book377528.pdf sample is the fallback file.
9. om: the text damage is understated.
10. pw: the index timeout was not reproduced.
11. au: "VERIFIED text" was not reproducible.
