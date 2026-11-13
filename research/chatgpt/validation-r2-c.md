# Validation of ChatGPT's round-2 shortlist (research/chatgpt/r2_c.md)

**Checked on:** 2026-11-07, from a UK network.

**Client:** the repo's `world_legal_mcp._http`. It sent our real UA, `Fontes/0.1.0 (+https://github.com/ykarapazar/fontes)`, with no faked headers, spaced requests at least 1.3 s apart per host, and made a handful of requests per site. No sign-ups, no logins, no challenge circumvention.

**Status labels:**
- **UNVERIFIED** means I could not check the item; the reason is given each time.
- **Not legal advice.** Terms quotes are reproduced as found. Whether a site's terms actually bind is not assessed.
- **Unofficial** sources are allowed if their terms permit it, and are labelled as such.

---

## mn — legalinfo.mn (legislation, official) — **GO-WITH-CAVEAT**

1. **Reachable:** yes. `/mn/about/16106883680221` (the "ЭЗМНС - ийн журам" rules page), the rules PDF, `ajaxList` and a detail page all returned 200. `robots.txt` returned 404 (HTML error page), so there are no robots rules.
2. **Search:**
   - `POST https://legalinfo.mn/mn/ajaxList/` with form fields `title=Иргэний хууль&isvalid=1` returned JSON `{"Html", …}` with 13 `detail?lawId=` links, e.g. 299 "ИРГЭНИЙ ХУУЛЬ", 180, 11954, 16532152438661.
   - The same route as in round 1; it still works.
3. **Text:** HTML. `GET /mn/detail?lawId=16230709635751` (ХӨДӨЛМӨРИЙН ТУХАЙ /Шинэчилсэн найруулга/, the revised Labour Law, 2.2 MB page): "1 дүгээр зүйл.Хуулийн зорилт … 1.1.Энэ хуулийн зорилт нь хөдөлмөрийн харилцааны зарчим, суурь хэм хэмжээг тогтоож…"
4. **Terms and robots:**
   - **The rules PDF is a scan.** https://legalinfo.mn/storage/uploads/process/202602/file_1770627213602915_163403209487511.pdf returned 200 (4.55 MB, 12 pages). Producer "KONICA MINOLTA bizhub 284e", no fonts, one 200-dpi JPEG per page, and `pdftotext` gives 12 bytes. There is no text layer.
   - **OCR:** tesseract with `mon+rus` was already installed, so I OCR'd the PDF locally. The quotes below come from that OCR, so they may contain OCR slips.
   - **What the PDF is:** a Minister of Justice and Home Affairs order (signed Б.ЭНХБАЯР) that approves the "Эрх зүйн мэдээллийн нэгдсэн сан бүрдүүлэх, ашиглах журам" (procedure for compiling and using the unified legal information database). The order's date did not OCR cleanly.
   - **Key clause, 1.2:** "Эрх зүйн мэдээллийн нэгдсэн сан … нь олон нийтэд нээлттэй, үнэ төлбөргүй байна." ("The unified legal information database shall be open to the public and free of charge.")
   - **Clause 1.3:** the servers, software and database are the property of the Ministry.
   - **Prohibitions, ch. 8 (Найм. Хориглох зүйл):** these bind only the institutions that hold login access (President's Office, Constitutional Court, Supreme Court, parliament, ministries, …). They ban sharing passwords, password crackers, remote-control tools, protocol analysers ("сүлжээний протокол задлагч программыг ажиллуулах"), using others' credentials, and unlicensed software.
   - **What it does not contain:** no clause on public reuse, copying, automated access, commercial use or AI.
   - **Footer:** "Бүх эрх хуулиар хамгаалагдсан." ("All rights protected by law.")
5. **Coverage:** site counters as recorded in round 1: 956 laws and 20,048 acts in total. Mongolian, plus 347 unofficial English translations.
6. **Caveat:** the official procedure says the database is open and free to the public, but it grants no reuse licence, and the footer reserves rights. Nothing forbids automated reading by the public. The gate ChatGPT named, "read the PDF", is now done, and there are no blockers in it.
7. **ChatGPT errors:**
   - It said the PDF "could not be read in this round; web retrieval returned 403". With our client it returned 200. The real obstacle is that it is a scan, which ChatGPT did not say.

## ng — nipc.gov.ng Acts (legislation, official) — **GO-WITH-CAVEAT**

1. **Reachable:** yes, all 200, no challenge.
2. **Listing (no search):**
   - `GET https://nipc.gov.ng/external-resources/document-types/act`, plus `?page=2` and `?page=3`.
   - Those pages hold 15 + 15 + 8 = **38 Acts**. Each card links straight to `/assets/resources/{slug}/{file}.pdf`, e.g. `/assets/resources/nigeria-tax-act-2025/nigeria-tax-act-2025-gazette.pdf`.
   - No search form or parameter was found, so the adapter would list the 3 pages and filter locally.
3. **Text:** text-layer PDFs.
   - Nigeria Revenue Service (Establishment) Act 2025: 32 pages, "Microsoft: Print To PDF", "PART II – ESTABLISHMENT OF THE NIGERIA REVENUE SERVICE … 6. Establishment of the Governing Board".
   - Industrial Inspectorate Act 1970: 8 pages, Acrobat Distiller, 18.7 KB of text, "INDUSTRIAL INSPECTORATE ACT ARRANGEMENT OF SECTIONS … Establishment and composition of Industrial Inspectorate Division."
4. **Terms and robots:**
   - robots (https://nipc.gov.ng/robots.txt): `User-agent: *` / `Disallow:` / `Sitemap: https://nipc.gov.ng/sitemap.xml`. Nothing is disallowed.
   - Footer: "© 2026 Nigerian Investment Promotion Commission. All rights reserved." The only footer links are "NIPC Email" and "Recruitment Policy".
   - No terms, licence or AI clause was found.
5. **Coverage:** 38 business-relevant federal Acts, in English, from the 1970 Acts to the 2025 tax Acts. Examples: CAMA, Labour Act, Land Use Act, FOI Act, Immigration Act, Petroleum Industry Act, Copyright Act 2022, Nigeria Tax Act 2025. This is a subset, not the Laws of the Federation.
6. **ChatGPT errors:** none. Its estimate of "roughly 30–45" was right (38).

## kh — ECCC (case law, official, tribunal-only) — **GO-WITH-CAVEAT**

1. **Reachable:** yes.
   - www.eccc.gov.kh: `/en`, `/en/cases/case-001`, F28_EN.PDF (21.6 MB) and the Practice Direction all returned 200.
   - archive.eccc.gov.kh: `/en`, a document page and `/api/documents/…` returned 200. Its `robots.txt` returned **500** (a Next.js error page).
2. **Listing and search:**
   - **Listing:** `GET https://www.eccc.gov.kh/en/cases/case-001` links about 445 PDFs under `/sites/default/files/documents/`, e.g. `F28_EN.PDF`, `F28_FR.pdf`, `F28_KH.PDF`, `E188_EN.PDF`. These are mixed: judgments, filings and UN reports.
   - **Metadata:** the archive app uses `GET https://archive.eccc.gov.kh/api/documents/981006?matterId=49`, which returns JSON: `{"doc_no":"F28","record_type":"Judgment","title_en":"[Corrected 1] Appeal Judgement of Case 001","doc_date":"03/02/12","classification":"Public","pagecount":350,…}`.
   - **Search:** the archive search (`/search?matter=judicial&key=…`) is a JS app. Its API is UNVERIFIED (not probed).
3. **Text:**
   - The F28 PDF is a scan with an invisible OCR text layer (ZyLAB export, font "InvisibleMonospacePdf"), 350 pages.
   - The text is readable but fragmented: "The Supreme Court Chamber of the Extraordinary Chambers in the Courts of Cambodia … hereby renders its Judgement on the appeals against the Judgement of the Trial Chamber … in the case of KAING Guek Eav alias Duch".
   - Expect broken lines and OCR noise.
4. **Terms and robots:**
   - robots (https://www.eccc.gov.kh/robots.txt) is the single line `User-agent: *`, with no rules.
   - archive.eccc.gov.kh has no usable robots file (500), and its pages carry `<meta name="robots" content="noindex">`.
   - The Practice Direction on Classification, art. 12.3 (https://www.eccc.gov.kh/sites/default/files/legal-documents/6-PD%20on%20Classification%20EN%20Rev2%20.pdf) says: "Materials classified as public may be accessed by the public. However, any such materials that are under copyright or subject to an agreement with a third party that prohibits dissemination shall not be released to the public, unless permission is granted by the third party."
   - No site terms, © line or AI clause was found on the homepage.
5. **Coverage:** ECCC Cases 001, 002, 003 and 004 only, in EN, KH and FR. Not Cambodian domestic case law. The adapter `kh.py` is CDC legislation, so this would add case law.
6. **ChatGPT errors:** none. It missed the archive JSON metadata API and the archive's `noindex` and robots 500 (omissions, not counted).

## ng — nass.gov.ng (legislation, official) — **GO-WITH-CAVEAT (low value)**

1. **Reachable:** yes, all 200.
2. **Listing:**
   - The "Acts & Publications" table on `/documents/magazine` is filled by DataTables from `GET https://nass.gov.ng/documents/magazine_track/?draw=1&start=0&length=10`.
   - That returned `{"recordsTotal":171,…,"data":[["ELECTORAL ACT, 2026","2026-05-13","NASS","10th Parliament","1st Session","Magazine","11248"],…]}`. The last field is the `/documents/download/{id}` id.
   - **Search does not work:** `search[value]=torture` and `search[value]=Act` both return the same unfiltered 171 rows.
   - The 171 rows are mixed. They include Acts, a Bill ("JOINT REVENUE BOARD … BILL, 2025"), a "Motion", "NASS OPEN WEEK 2026" and a handbook.
3. **Text:**
   - `GET /documents/download/11248` returned a 121-page Ghostscript PDF with a text layer: "ELECTORAL ACT, 2026 ARRANGEMENT OF SECTIONS … PART I – ESTABLISHMENT AND FUNCTIONS OF INDEPENDENT NATIONAL ELECTORAL COMMISSION".
4. **Terms and robots:**
   - `https://nass.gov.ng/robots.txt` returns the homepage HTML (same md5 as `/`), so there are no robots rules.
   - The footer "Terms" and "Privacy Policy" links are `href="#"`.
   - No terms were found.
5. **Coverage:** 171 publications, only a minority of them Acts. Most are recent (the 2025 tax Acts, the Electoral Act 2026), with some older ones (Anti Torture Act 2017, 2018 Appropriation Act).
6. **ChatGPT errors:**
   - It said the Acts listing "opened with an empty table; no functioning search/API established". The table loads from a working JSON endpoint with 171 rows. Only text search is non-functional.

## eg — GAFI virtual library (legislation, official) — **NO (not worth an adapter)**

1. **Reachable:** yes. `gafi.gov.eg/en/booklet` and the PDF returned 200.
2. **Listing:**
   - `GET https://gafi.gov.eg/en/booklet` shows "17" results, but only **3 PDF links** in the HTML: Companies Law 159 AR, Investment Law 72 AR and an Arabic facts-and-figures brochure.
   - No search API was found.
3. **Text:**
   - The Companies Law PDF (InDesign CS3, 132 pages, 228 KB of text) has a text layer, but it is **systematically damaged**.
   - Running heads come out as mojibake: "ŹřŶƇœƱŐƄŝÎ".
   - Body text has broken Arabic letter order throughout: "اجلريدة الرمسية" for الجريدة الرسمية, "املرافق" for المرافق, "اجلمهوري ـة". Quotes would be wrong unless repaired or OCR'd.
   - Its amendment list ends at "4 لسنة 2018".
4. **Terms and robots:**
   - https://gafi.gov.eg/robots.txt: `User-agent: *` / `Allow: /` / `Sitemap: https://gafi.gov.eg/sitemap.xml`.
   - https://gafiadmin.gafi.gov.eg/robots.txt: 404 ("Status Code: 404; Not Found").
   - Footer: "Copyright © August 2026 Egypt is Paving the Way - GAFI". No terms or policy links were found.
5. **Coverage:** effectively 2 laws (Companies 159/1981, current to 2018; Investment 72/2017), in Arabic. This does not fill eg's legislation gap.
6. **ChatGPT errors:**
   - "Substantial extractable Arabic text, although some headings are garbled" understates it: the body text is damaged throughout, not just the headings.

## bt — judiciary.gov.bt (case law, official) — **NO (for now)**

1. **Reachable:** no. `https://judiciary.gov.bt/robots.txt`, `/archive-content/judgments` and `/archives/1697536320-.pdf` all failed with `ConnectTimeout`.
   - `https://www.judiciary.gov.bt/robots.txt` and `http://judiciary.gov.bt/robots.txt` also timed out.
   - DNS resolves to 43.230.208.73, but `nc -z` to port 443 failed. The TCP connection is not accepted from our network.
2. **Search, text, terms, robots, coverage:** UNVERIFIED (unreachable).
3. **ChatGPT errors:**
   - "VERIFIED through web opening: archive and two PDFs" / "23-page text-readable PDF" could not be reproduced with our client.
   - ChatGPT's robots timeout matches what we saw.
4. **Option:** re-test from a non-UK network. Its claimed metadata mismatch (wrong PDF behind a title) is UNVERIFIED.

## FAOLEX (np, kg) — faolex.fao.org (legislation, **unofficial**, intergovernmental) — **NEEDS-PERMISSION (for commercial users)**

1. **Reachable:** yes, all 200.
2. **Search and listing:**
   - robots disallows `/?filters=`, which appears to be the site's search-filter route (UNVERIFIED that it is the only search route). So search is off-limits.
   - Listing is via the allowed sitemaps: `https://faolex.fao.org/sitemaps/documents.xml` is an index of `documents-1.xml` … `documents-5.xml` (not fetched).
   - Record pages (`/en/documents/LEX-FAOC219736/…`) are an 11.6 KB JS shell, with canonical links on `www.fao.org/faolex/…`.
3. **Text:**
   - `https://faolex.fao.org/docs/pdf/kyr219736.pdf`: 249 pages, text layer. "CIVIL CODE OF THE KYRGYZ REPUBLIC (As amended by the Laws of the Kyrgyz Republic of April 29, 1997 # 29 and October 15, 1997 # 76)". This is current only to 1997.
   - `https://faolex.fao.org/docs/pdf/nep209663.pdf`: 13.4 MB, 404 pages, Word 2013. "If a person already declared dead pursuant to sub-section (4) comes back alive and files a petition…"
4. **Terms and robots:**
   - robots (https://faolex.fao.org/robots.txt): `User-agent: *` / `Disallow: /design-system/` / `Disallow: /?filters=` / two Sitemap lines.
   - FAO Terms and Conditions (https://www.fao.org/contact-us/terms/en/), "REUSE OF WEB CONTENT":
     - "All other content on the FAO website (except where otherwise indicated), may be copied, printed and downloaded for private study, research and teaching purposes, and for use in non-commercial products or services, provided that appropriate acknowledgement of FAO as the source and copyright holder is given and that FAO's endorsement of users' views, products or services is not stated or implied in any way."
     - "All requests for translation and adaptation rights, and for resale and other commercial use rights should be addressed to [copyright e-mail] or submitted via the online Licence Request Form".
     - "Third-party content—FAO does not necessarily own each component of the content … If you wish to re-use a component of the work, it is your responsibility to determine whether permission is needed for that re-use and to obtain permission from the copyright owner."
   - No automation or AI clause.
   - **What this means for Fontes:** Fontes itself is free, non-commercial software, which fits "use in non-commercial products or services". But a company using Fontes in paid work falls outside that grant, and the terms say commercial-use rights must be requested. The translations may also be third-party content. A safe ship would be either an FAO licence or a per-result "non-commercial use only, © FAO" label that leaves compliance with the user. That choice is for the owner.
5. **Coverage:** selected national texts, often English translations, and often outdated (the kg Civil Code stops at 1997). Unofficial.
6. **ChatGPT errors:**
   - It said commercial use "require[s] additional attention". The terms actually require a rights request to FAO for commercial use (understated).
   - It did not flag that `/?filters=` (search) is robots-disallowed (omission, not counted).

## id — putusan3.mahkamahagung.go.id — **NO**

- `/direktori.html` returned **403 with a Cloudflare "Just a moment… Enable JavaScript and cookies" challenge**.
- robots (https://putusan3.mahkamahagung.go.id/robots.txt) has the Cloudflare `User-agent: *` / `Content-Signal: search=yes,ai-train=no,use=reference` / `Allow: /` block, and then, further down, the site's own groups. Those include `ChatGPT-User` and `ClaudeBot` with `Disallow: /`, and "# Everything else — block by default" / `User-agent: *` / `Disallow: /`.
- **ChatGPT error:** it quoted only the Cloudflare block and said the blanket disallow "should not be repeated as current". It is still there.

## hk — HKLII — **NO**

- robots (https://www.hklii.hk/robots.txt) is `User-agent: *` / `Disallow: /api`.
- `/legal` returned a 2.7 KB JS shell, so ChatGPT's quote "HKLII specifically blocks all spiders and other automated agents…" stays UNVERIFIED directly.
- The data is only reachable through `/api`, which robots disallows.
- ChatGPT already flagged its quote as search-index evidence, so this is not counted as an error.

---

## Summary

| source | verdict | one-line reason |
|---|---|---|
| mn legalinfo.mn | GO-WITH-CAVEAT | Rules PDF is a 12-page scan; OCR shows the database is "open to the public and free of charge" (§1.2), with prohibitions aimed only at logged-in institutions; no reuse licence; footer "all rights protected" |
| ng nipc.gov.ng | GO-WITH-CAVEAT | 38 business Acts across 3 list pages, direct text PDFs, robots open; "All rights reserved", no terms; subset only |
| kh ECCC | GO-WITH-CAVEAT | Tribunal-only; case pages list about 445 PDFs; archive JSON metadata; OCR text layer; PD art. 12.3 public access; robots empty |
| ng nass.gov.ng | GO-WITH-CAVEAT (low value) | Hidden DataTables JSON lists 171 mixed publications (search ignored); text PDFs; no robots, placeholder terms |
| eg GAFI | NO | Effectively 2 laws; Companies Law current only to 2018; Arabic text layer systematically damaged |
| bt judiciary.gov.bt | NO (for now) | ConnectTimeout on every request (TCP 443 refused/dropped from UK); nothing verifiable |
| FAOLEX np/kg | NEEDS-PERMISSION | FAO terms allow only non-commercial use; commercial use requires a rights request; unofficial and often outdated (kg Civil Code to 1997); search robots-disallowed |
| id putusan3 | NO | Cloudflare JS challenge (403); robots still ends `User-agent: *` / `Disallow: /` |
| hk HKLII | NO | JS shell; data only via robots-disallowed `/api`; terms quote unverifiable directly |

**ChatGPT errors found: 6.**
1. mn: the rules PDF was "403, unreadable". It returned 200; it is a scan (now OCR'd).
2. ng NASS: "empty table; no functioning search/API". A JSON listing endpoint works (171 rows).
3. eg GAFI: text damage is understated; it is systematic in the body, not just "some headings".
4. bt: "VERIFIED archive and two PDFs" / "text-readable PDF" was not reproducible (ConnectTimeout).
5. FAOLEX: commercial use "requires additional attention". The terms actually require a rights request.
6. id: robots was reported as `Allow: /`, with the claim that the blanket disallow is gone. The site's own `User-agent: *` / `Disallow: /` is still in the file.
