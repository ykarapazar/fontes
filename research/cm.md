# Cameroon (cm) — source notes (checked 2026-11-06)

| Host | Use | robots.txt | Terms | Auth | Result |
|---|---|---|---|---|---|
| coursupreme.cm (Cour suprême) | case law | 404 (no rules) | none published; footer "Copyright © 2019 CSC. All Rights Reserved" | none (login exists for other services; judgments are public) | **built** |
| www.coursupreme.cm | — | — | — | — | TLS certificate is for coursupreme.cm only (hostname mismatch); not used |
| www.prc.cm (Présidence) | legislation | Joomla default: only system folders (/administrator/, /components/, /media/, ...) disallowed; no Crawl-delay | none; "Règles de confidentialité" page is empty; footer "Tous droits réservés" | none | **built** |
| www.minjustice.cm (LÉGALIS) | — | allows / (except /admin, /storage, /contributions) | — | none | not used: Lois 2 docs, Décrets PR 1, Jurisprudence 0 (2026-11-06) |
| www.assnat.cm | — | Joomla default | — | — | not examined further (Presidency publishes the promulgated text) |
| www.spm.gov.cm | — | 404 | — | — | not examined further |
| conseil constitutionnel | — | — | — | — | no official site found (conseilconstitutionnel.cm, conseil-constitutionnel.cm, cccameroun.cm do not resolve) |
| www.minjustice.gov.cm | — | — | — | — | connection failed |

Cour suprême: GET /search?critere=Q&lang=fr|en&page=N (0-based, 9 a page) full-text search, indexed
per language. Each judgment has a French and an English page (different slugs); the body sits only
in the original language. A few dozen judgments (2019-2024), plus PDFs under /images/webcsc_medias/files/.
Listing dates on the site are upload dates (all "6 novembre 2026"); decision dates come from titles.

Présidence: Smart Search /fr/chercher?q=&limit=50&start=; category blogs /fr/actualites/actes/{lois,
ordonnances,decrets}?start= (8 a page, limit param ignored). Article URL by id /fr/actualites/actes/<id>.
Up to ~2014 the act text is HTML; later acts are a page image + PDF (some with an OCR text layer,
many pure scans). PDF HEAD needs Accept-Encoding: identity to get Content-Length (served gzip otherwise).
