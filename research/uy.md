# Uruguay (uy): source notes, checked 2026-11-05

## IMPO (www.impo.com.uy), legislation
- Open data: add `?json=true` to any `/bases/{base}/{num}-{year}[/{article}]` URL. The reply is ISO-8859-1 with raw CR/LF inside strings.
- Licence: the Datos Abiertos page (https://www.impo.com.uy/datos-abiertos/) says that since July 2018 the public information in the bases is open data under the "Licencia de Datos Abiertos – Uruguay v0.1". That licence allows commercial use if you credit IMPO, the licence and the dataset.
- Conflict: the "Condiciones de Uso del Banco de Datos" (https://www.impo.com.uy/politica-de-privacidad-y-seguridad/) say "El uso de la información suministrada es personal e intransferible, quedando prohibida su copia, reproducción o cesión a terceros, así como su comercialización". IMPO also sells subscriptions (/cgi-bin/suscripcion). Which documents are subscription-only is unverified.
- robots.txt: `User-agent: *`, `Crawl-Delay: 10`. It disallows /cgi-bin/ (all of IMPO's search, including `/bases` → `principalBases.cgi`), /descargas, /java, /js, /skin and similar. /bases/... norm pages are allowed. There is no AI-specific rule.
- Unknown id: HTTP 200 with an HTML "Acceso no válido … no posee ningún servicio vigente" page, the same page IMPO shows for paywalled content.
- Size: the Código Civil JSON is 1.7 MB and took about 2 minutes from the UK; one article is about 2 KB and takes about 1 s.

## BJN (bjn.poderjudicial.gub.uy/BJNPUBLICA), case law
- robots.txt: 404. No terms or licence page was found. The 2012 user manual says "accedido libremente, sin necesidad de login".
- Technology: JBoss Seam/RichFaces. Searches and opening a decision are A4J AJAX POSTs in a server session, followed by GET `hojaInsumo2.seam?cid=N`. There are no permalinks.
- Ids: "número | sede | fecha", because número + sede is not unique.
- Index lag: the newest decision was dated 2026-09-11, about 2 months behind. Anonymisation is inconsistent.

## Not used
- parlamento.gub.uy: CloudFront 403 to a plain client.
- catalogodatos.gub.uy: robots.txt disallows /api/. I sent one request there by mistake before reading robots.txt.
