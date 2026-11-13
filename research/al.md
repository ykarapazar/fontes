# Albania (al) — source research, 2026-11-05/06

## qbz.gov.al — Qendra e Botimeve Zyrtare (Ministry of Justice; law 78/2014) — USED (legislation)
- robots.txt (2026-11-05): none; /robots.txt returns the SPA index.html (HTTP 200), so no rules.
- Terms: no terms page. FAQ (/faq): "Informacioni i publikuar është i aksesueshëm nga publiku i gjerë
  pa asnjë lloj kufizimi." = "The published information is accessible to the general public without
  any restriction." Licence, commercial use and AI/TDM: not stated.
- API: https://qbz.gov.al/api/v1 (no auth): /acts?q=&type=&from=&to=&page=&size=, /acts/{id},
  /acts/{id}/versions, /eli?path=, /acts/types. Files: /files/{sha}.docx|.doc, /pdf/{sha}.pdf.
- Not used: /publications?type=kode (priced editions, priceLek).
- Gap: 1990s base codes (Civil 7850/1994, Penal 7895/1995, Labour 7961/1995) are not in the archive.

## gjykataelarte.gov.al — Gjykata e Lartë (High Court) — USED (case law)
- robots.txt (2026-11-05): none on www/apex (redirect to /sq/), JSON 404 on be.gjykataelarte.gov.al,
  403 on the S3 bucket vendimet-perfundimtare.s3.eu-central-1.amazonaws.com.
- Terms (/sq/termat-e-perdorimit): "Përdorimi i faqes së internetit është falas dhe është në
  dispozicion të gjithë përdoruesve në mbarë botën." = "Use of the website is free and available to
  all users worldwide." Only unlawful use is forbidden. Silent on automation, licence, commercial, AI.
- API: https://be.gjykataelarte.gov.al/public/ documents/search, filterVerdicts, verdict (presigned
  S3 URL to .doc/.docx). x-ratelimit-limit: 50 header (window unknown).
- Decisions are not anonymised.

## gjykatakushtetuese.gov.al — Constitutional Court — NOT BUILT
- robots.txt (2026-11-05): Disallow /wp-admin/, /wp-content/uploads/wpforms/, /imunify-bot-check only.
- No terms page found. Decisions are monthly WordPress pages with PDFs; the REST court_decision
  type returned 0 on search. Imunify bot-check present. Possible later source.
