# Venezuela (ve): source check, 2026-11-06

No adapter built. Checked from a UK IP with the project User-Agent, all through `_http`,
about 20 requests in total. robots.txt read first on every host that answered.

## Tribunal Supremo de Justicia (case law): `www.tsj.gob.ve`, `historico.tsj.gob.ve`
- `https://www.tsj.gob.ve/robots.txt` and `https://historico.tsj.gob.ve/robots.txt`:
  ConnectError (no TCP/TLS connection). `http://` on both: ReadError (connection reset).
- Consistent with the TSJ refusing connections from outside Venezuela. Not retried.
  Terms not readable. → UNREACHABLE. No other official case-law source found.

## Asamblea Nacional (legislation index): `www.asambleanacional.gob.ve`
- robots.txt (2026-11-05/06): `User-agent: * / Disallow:` (everything allowed).
- `/leyes/vigentes` answered 200 with a list (title, Gaceta Oficial number, filter form
  `titulo`, `gaceta_oficial`, `materia`, `fecha_publicacion_inicial`; forms carry an
  `AFHTOKEN` anti-form-hijack field), 49 pages.
- `/leyes/vigentes?page=2` (the site's own pagination link) answered **HTTP 403 Forbidden**
  (plain Apache page). Per the rules a 403 means the host is not used; not retried.
  → BLOCKED (WAF/403 on query strings).

## Gaceta Oficial (official gazette): `www.gacetaoficial.gob.ve` — the promising one
- robots.txt: `User-agent: * / Disallow:` (everything allowed). No terms page found on the
  site (no footer links; nothing on automation).
- Laravel site, plain HTML, no login:
  * `/` calendar of issues per year (2010–2026), `?year=YYYY`.
  * `/gacetas/dia?year=&month=&day=` JSON list of the day's issues.
  * `/gacetas/filtro-avanzado?texto=…` (also `numero_exact`, `numero_gaceta_desde/hasta`,
    `fecha_desde/hasta`, `organo`, `titulo`, `pagina`): full result table, no server paging
    (DataTables client-side). Columns: Nro Gaceta ("43.226"), Tipo (ORDINARIA /
    EXTRAORDINARIA), Título, Fecha (dd/mm/yyyy), Página inicio/fin, Status.
    `texto=Archivos` → 14 issues back to 2012.
  * `/gacetas/{numero}` issue page: metadata + "Sumarios" table (Órgano, Ente adscrito,
    Título of each act, página inicial/final in the gazette's running page numbers) and
    the issue PDF at `/storage/{year}/{numero}-{yyyy-mm-dd}-{TIPO}.pdf`.
- Would map well: law_id = gazette number, TOC = sumarios, provision = the act's PDF pages.
- **Why not built:** after ~9 requests (default 0.25 s spacing) the host stopped answering
  me: HEAD and a ranged GET on the issue PDF, then plain HTML pages and robots.txt, all
  ReadTimeout (60 s), still after a 90 s pause and again after ~10 minutes. Could be an
  IP-level drop (rate block) or an outage; can't tell which from here. Not retried beyond
  those two spaced checks. PDF size and text layer were never confirmed.
  → Re-check later (from a fresh IP, with ≥ 3 s spacing). If the host answers steadily
  and the PDFs have a text layer, a legislation adapter is ~1 day of work.

## Imprenta Nacional (`www.imprentanacional.gob.ve`)
- `http://` robots.txt 404 (no rules); `https://` connection refused.
- Home links the "SUSCRIPCIÓN DIGITAL" (paid gazette subscription), a certificate
  validator, and `spgoin.imprentanacional.gob.ve/cgi-win/be_alex.cgi` (timed out).
  → Paid / unreachable. Not used.

## Others
- `www.pgr.gob.ve` (Procuraduría General): TLS certificate fails verification
  ("unable to get local issuer certificate"). Not patched. Not used.
