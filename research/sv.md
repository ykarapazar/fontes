# El Salvador (sv): source check, 2026-11-06

No adapter built. The two official sources that hold searchable case law and legislation
are both unreachable for an honest non-browser client, and the only open host (the Diario
Oficial) has no search and no per-law texts. Checked from a UK IP with the project
User-Agent, a handful of requests in total, all through `_http`.

## Corte Suprema de Justicia / Centro de Documentación Judicial (case law + consolidated laws)
- `www.jurisprudencia.gob.sv` (CDJ: Sala de lo Constitucional, Civil, Penal, Contencioso
  rulings; also the CDJ consolidated-legislation index) and `www.csj.gob.sv`.
- Both answered `GET /robots.txt` with HTTP 403 and a Cloudflare "Attention Required!
  | Cloudflare" block page. Not retried (rule: a WAF block means don't use the host).
  Terms could not be read for the same reason.
- `www.pgr.gob.sv` (Procuraduría General) returns the same Cloudflare 403.
- → BLOCKED (bot protection). This is the source that matters: if the CSJ ever allows
  the project User-Agent through Cloudflare, jurisprudencia.gob.sv should be re-checked
  first.

## Asamblea Legislativa (`www.asamblea.gob.sv`, legislation)
- TLS: the server sends only its leaf certificate (`CN=*.asamblea.gob.sv`, issued by
  `Sectigo Public Server Authentication CA OV R36`) without the intermediate, so
  verification fails ("unable to verify the first certificate"). Browsers paper over this
  with AIA fetching; Python does not. Not patched, not used, robots.txt not readable.
- → BLOCKED (incomplete certificate chain). Fix is on their side (serve the full chain).

## Diario Oficial (`www.diariooficial.gob.sv`, Imprenta Nacional)
- robots.txt: `User-agent: * / Disallow:` (everything allowed). No terms page found.
- Page `/` uses `POST /api/v1/meses-disponibles {year}` and
  `POST /api/v1/diarios-disponibles {year, month}`, which return only
  `{"Id","FechaInicio","NombreArchivo":"03-01-2025.pdf"}` per issue; the download is
  `/seleccion/{Id}` (whole-issue PDF). No titles of the laws inside, no text search.
- Can't meet the legislation contract (search by query, provisions): it would mean
  downloading whole multi-hundred-page issues to find anything. Not built.
- `imprentanacional.gob.sv` (WordPress): robots.txt allows all, but the REST API answers
  401 "Only authenticated users can access the REST API".

## Others looked at
- `www.transparencia.gob.sv` (IAIP portal): robots.txt 404 (no rules). A store of
  institutional disclosure documents, not a legislation or case-law database.
- Ministerio de Hacienda (`www.mh.gob.sv`, robots allows all; `transparencia.mh.gob.sv`):
  no searchable index of tax tribunal (TAIIA) rulings found.
- `www.fiscalia.gob.sv`, `www.cnj.gob.sv`: robots.txt readable, no legal database.

## If things change
1. jurisprudencia.gob.sv lets the project UA through → case law (and CDJ legislation index).
2. asamblea.gob.sv serves a complete chain → legislation search (decree texts, mostly PDF).
