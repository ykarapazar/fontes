# Bolivia (bo): blocked or unbuilt sources (checked 2026-11-05/06)

- **Tribunal Constitucional Plurinacional**: buscador.tcpbolivia.bo (Angular SPA, no robots.txt).
  Its /api/... endpoints answer 401 unless the request carries X-Timestamp, X-Hash (a hash the app
  computes per request) and X-Client-ID "angular-app"; the app also has a captcha component.
  This is anti-automation, so not used. tcpbolivia.bo, www.tcpbolivia.bo and jurisprudencia.tcpbolivia.bo
  timed out or refused connections.
- **Tribunal Supremo de Justicia**: genesis.tsj.bo is a Vue SPA on apigenesis.tsj.bo/api/v1/
  (e.g. POST jurisprudencia/busqueda_simple). It returns 401 without the headers `username: buscadorgenesis`
  and an `apikey` hard-coded in the public JS. Not used: that would impersonate the official client.
  Needs an API grant from the TSJ (env var would be WLM_BO_TSJ_KEY). tsj.bo robots only disallows /wp-admin/.
- **Gaceta Oficial**: gacetaoficialdebolivia.gob.bo did not resolve via the local resolver (public DNS gives
  181.115.190.188); www. does not resolve. Not verified. Retry later from a network that resolves it.
  This would give consolidated/official legislation beyond diputados.gob.bo's 2010–2023 range.
- **Senado** (senado.gob.bo): robots allows all; not explored.
- **diputados.gob.bo**: there is also a ninja-tables endpoint (table 4760, ~900 KB in one response).
  The WP REST API (`/wp-json/wp/v2/ley`) was chosen instead.
