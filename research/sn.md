# Senegal (sn): source findings, 2026-11-05/06

## Used
- **conseilconstitutionnel.sn** (Conseil constitutionnel, WordPress). robots.txt: `User-agent: * / Disallow: /wp-admin/ / Allow: /wp-admin/admin-ajax.php`. No terms or legal-notice page found. REST API `/wp-json/wp/v2/docs` (decisions, 41 posts) and `/wp-json/wp/v2/pages?slug=la-constitution` (consolidated Constitution, modified 2024-02-09).
  - Most decisions are embedded PDFs. Every PDF checked (2023, 2024, 2025 and 2026) is a scan with no text layer, sized 0.8 to 14.5 MB. Only 5/E/2019 and 21/E/2022 are HTML text. 2/C/2026 is a file-download block.
  - The host is slow and unreliable: read and connect timeouts after about 25 requests on 2026-11-06, with no 403 or 429. Spacing is 1.5 s.
- **primature.sn** (Primature / Secrétariat général du Gouvernement, Drupal; www.sec.gouv.sn redirects here). robots.txt is the Drupal default and disallows `/search/`, so the adapter lists `/publications/lois-et-reglements/{lois-et-decrets,codes}` and filters locally. No terms page; the footer says "© Primature 2024".
  - About 40 laws and decrees as HTML text. The 18 code pages only hold an exposé des motifs. Their PDF attachments (`/sites/default/files/2022-04/...`) answered 404 on HEAD.

## Not used
- www.jo.gouv.sn (Journal officiel): connection timeout over both http and https. jo.gouv.sn does not resolve (NXDOMAIN).
- www.coursupreme.gouv.sn (Cour suprême): the site shows a "Plateforme en cours d'optimisation" maintenance page (Sénégal Numérique). robots.txt returns 404. coursupreme.sn is a parked domain.
- justice.sec.gouv.sn (Ministry of Justice): robots.txt allows everything, but the /publications/textes/ page timed out.
- www.sgg.sn: TLS hostname mismatch. www.justice.gouv.sn: TLS chain error. The rules say not to bypass TLS, so neither was used.
- www.assemblee.sn: robots.txt allows crawling, but the homepage (7 KB, JS app) shows no law texts.
- www.vie-publique.sn: full Journal officiel PDF archive, but it is a civic NGO/association, so not official. Documents are public domain, editorial content is CC BY 4.0, and robots.txt sets `Content-Signal: search=yes,ai-input=yes,ai-train=no,use=reference`. It could be added later as a flagged non-official source.

## Reliability (2026-11-06)
- At 10:05 the conformance run passed 6/6. From about 10:07 every request to conseilconstitutionnel.sn timed out on read or connect for at least 45 minutes, across 4 runs spaced several minutes apart. No 403, 429 or block page was returned. The cause is unknown: an outage, or a silent firewall tarpit after roughly 30 requests.
- primature.sn returned 503 once on a listing page and passed on retry.

## Recheck and additions, 2026-11-10
- www.coursupreme.gouv.sn: still the "Plateforme en cours d'optimisation" maintenance page (http and https, www and bare).
- www.jo.gouv.sn: connect timeout over http and https; jo.gouv.sn NXDOMAIN.
- **justice.sec.gouv.sn** (Ministry of Justice, WordPress) is now used. Its "Textes" page shows only category headings, but `/wp-json/wp/v2/media?mime_type=application/pdf` lists all 133 PDFs it hosts. About 60 are laws, codes, decrees and OHADA acts, all with a text layer: Code pénal and CPP (JURISCONSULT compilations with amendment notes), COCC, Code de la famille, Code du travail, Code gazier, Loi 2014-26 (organisation judiciaire), Lois 2017-10/11 (magistrates). robots.txt (Yoast) allows all; no terms page (`/mentions-legales/` 404).
- juricaf.org (unofficial, Cour suprême decisions): robots.txt lists ~100 AI agents by name (ClaudeBot, Claude-User, ChatGPT-User, ...). Not built (the slice did not ask for unofficial case law).
