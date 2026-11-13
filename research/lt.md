# Lithuania (lt): no adapter (checked 2026-11-05)

Every official source refuses automated readers, so no adapter was built. All checks used
the project User-Agent `world-legal-mcp/0.1.0 (+https://github.com/ykarapazar/fontes)`
and a handful of requests per host.

| Host | Role | Result 2026-11-05 |
|---|---|---|
| www.e-tar.lt | Register of Legal Acts (TAR) | 403 Cloudflare "Just a moment..." on every path, robots.txt included |
| e-seimas.lrs.lt | Seimas legal-act portal | 403 Cloudflare challenge, robots.txt included |
| get.data.gov.lt, data.gov.lt | Open-data Spinta API (TAR dataset `datasets/gov/lrsk/teises_aktai`) | WAF block page "Web Page Blocked!", Attack ID 20000018, robots.txt included |
| apps.lrs.lt | Seimas open-data XML (CC BY 4.0) | robots.txt `User-agent: * / Disallow: /`; parliamentary data only, not act texts |
| www.lrs.lt, www3.lrs.lt | Seimas site | robots.txt `Crawl-delay: 20`, `Disallow: /pls/` (old act viewer) |
| liteko.teismai.lt | Public court-decision search | robots.txt 404; page loads, but the search form has a Google reCAPTCHA (`g-recaptcha` next to the submit button) |
| www.lat.lt | Supreme Court | 403 Cloudflare challenge |
| www.lvat.lt | Supreme Administrative Court | 403 Cloudflare challenge |
| www.apeliacinis.lt | Court of Appeal | 403 Cloudflare challenge |
| www.lrkt.lt | Constitutional Court | 403 Cloudflare challenge |
| www.teismai.lt | Courts portal | 403 Cloudflare challenge |

Non-official sites seen and not used: infolex.lt (commercial; robots `Disallow: /` for `*`),
eteismai.lt (private aggregator).

Prior art: Ansvar-Systems/Lithuanian-law-mcp and simasrazinskas/istatym.ai both ingest TAR
from get.data.gov.lt (Spinta API) in bulk. That is the only API route.

Next step: retest get.data.gov.lt from another network. If the WAF block is per IP and the
open-data terms allow reuse, it could support legislation search + text.
