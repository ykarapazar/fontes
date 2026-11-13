# Dominican Republic (do): source notes, 2026-11-06 (UK IP, project UA)

Built: TSE (electoral court) judgments via visorpdf.tse.do. See `jurisdictions/do_.py`.

Blocked / not used:
- **Tribunal Constitucional** (tribunalconstitucional.gob.do, tc.gob.do): every path, including
  robots.txt, answers HTTP 406 "Azure Front Door was unable to process the request" to our UA.
  WAF filtering, so not used. Its sentencias dataset is listed on datos.gob.do (ODbL), but
  datos.gob.do robots.txt has `Disallow: /api/` and `Crawl-Delay: 10`, and the data is a bulk
  dataset.
- **Poder Judicial / SCJ** (poderjudicial.gob.do): 403 from Microsoft-Azure-Application-Gateway/v2.
  www.poderjudicial.gob.do times out. It may be geo-restricted, so it is worth retrying from a DO IP.
- **Consultoría Jurídica del Poder Ejecutivo** (consultoria.gov.do): robots.txt `Allow: /`.
  `GET /api/consultas/document-types` works, but `POST /api/consultas/search` (JSON body:
  DocumentTypeCode, FullText, PublicationYear, ...) returns a Cloudflare managed challenge, so
  the host is not used. Documents are at `/api/document/{DocId}`. Terms §3 prohibit "robots,
  scripts automatizados o técnicas de extracción no autorizada (scraping) que degraden el
  rendimiento". It is the best legislation source if its operator ever allows API access.
- **Senado** (senadord.gob.do): robots.txt disallows the named AI crawlers and sets
  `User-agent: * Crawl-delay: 120`. That is unworkable for on-demand use.
- **Cámara de Diputados SIL** (diputadosrd.gob.do/sil, JSON API at `/sil/api/iniciativa/...`):
  it has no robots.txt and its terms page is empty. It only covers bills of the current
  2024-2028 period. Enacted-law PDFs come from
  `s-sil.camaradediputados.gob.do:8095/ReportesGenerales/VerDocumento?documentoId=` and are
  scans with no usable text layer, and OCR is not allowed. It is not consolidated law.
