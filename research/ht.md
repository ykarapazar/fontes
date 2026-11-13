# Haiti (ht): source notes, 2026-11-05/06 (UK IP, project UA)

Built: legislation from the CSPJ (Conseil Supérieur du Pouvoir Judiciaire) document library,
cspj.ht, via the public WordPress REST API (`/wp-json/wp/v2/media?mime_type=application/pdf`).
22 PDFs in 2026-11, ~17 of them laws/decree-laws. 6 of those are scans with no text layer
(ids 1402, 1401, 1395, 1393, 1391, 1251); id 1392 has a poor OCR text layer from the uploader.
robots.txt: `User-agent: * / Disallow: /wp-admin/ / Allow: /wp-admin/admin-ajax.php`, no
Crawl-delay. No terms page; footer only "Droit d'auteur © 2026 Conseil Supérieur du Pouvoir
Judiciaire". See `jurisdictions/ht.py`.

Not used:
- **Cour de cassation** (www.courdecassation.ht, Cloudflare, no robots.txt (404), no terms page):
  `/consulter_arret/` has a search form (q, annee, categorie, section) but the database is
  empty ("Aucun arrêt trouvé", no categories). `/publication/` links 4 static PDFs
  (constitutions 1987 + amended, organisation judiciaire, CSPJ law). Re-check later: if the
  arrêts database fills, it is the case-law source.
- **Le Moniteur / Presses Nationales d'Haïti**: no live official site found (lemoniteur.gouv.ht,
  pressesnationales.gouv.ht, moniteur.ht etc. do not resolve).
- **budget.gouv.ht** (Direction Générale du Budget): hosts some Le Moniteur issues (budget/tax
  decrees) as PDFs, but the site is a maintenance page with no listing; no robots.txt (404).
- **Parlement** (parlementhaitien.ht): TLS certificate hostname mismatch; not used (no TLS
  workarounds). senat.ht / chambredesdeputes.ht do not resolve.
- **MJSP** (mjsp.gouv.ht): robots.txt allows all; WordPress with only informational pages and
  2 press-note PDFs. No legal texts.
- **Primature** (www.primature.gouv.ht): robots.txt allows all except wp-admin; no PDFs in media,
  posts are press releases.
- **laloidemabouche.ht** (private, non-official): bot challenge ("Checking your browser") on
  robots.txt itself. Not used.
- Non-official/academic archives of Le Moniteur (dLOC/UFDC, Gallica, SOAS) were not used
  (official sources only; scans).
