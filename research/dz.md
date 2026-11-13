# Algeria (dz) — source notes (checked 2026-11-05/06)

| Host | Use | robots.txt | Terms | Auth | Result |
|---|---|---|---|---|---|
| www.joradp.dz (SGG, Journal Officiel) | legislation | 404 (no rules) | none published (checked Help, Lien, Sgg, Note, Publi pages) | none | **built** |
| cour-constitutionnelle.dz | case law | `User-agent: * / Disallow:` (allows all) | none found | none | **not built**: server sends no intermediate certificate (Certum DV TLS G2 R39 CA), so `_http` fails TLS verification. WordPress REST `/wp-json/wp/v2/posts` with the decision categories returns all ~47 posts (decisions as `[vc_tta_section]` blocks) in one 1.8 MB call. Needs an `_http` change (e.g. trusting that intermediate) before an adapter can use it. |
| coursupreme.dz / www.coursupreme.dz | case law | — | — | — | timed out (http and https), twice |

JORADP details: search POST `/SCRIPTS/Jof_Rec.dll/RecPost` (session number from `/SCRIPTS/Jo_Con.dll/Fr`),
stateful paging via `AffPost` (`dfon=3`), keywords limited to the site's lexicon. Texts: issue PDFs
`/FTP/jo-francais/{y}/F{y}{jo:03}.pdf` from 1994; text layer only from ~2001; before 1994 per-page scans.
French edition is the official translation (Arabic authoritative). Not consolidated.

Recheck 2026-11-10: coursupreme.dz (http/https, www/bare), droit.mjustice.dz and www.mjustice.dz (http/https): all connect timeouts from the UK. Arabic JO issues `/FTP/jo-arabe/1990/A1990001.pdf` and `/2000/A2000001.pdf` and French `F1998001.pdf` have no text layer, so no pre-2002 text source exists on joradp.dz in either language.
