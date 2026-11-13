# Iraq (iq): source check, 2026-11-06 (UK IP, project User-Agent via `_http`)

| Host | What | Result |
|---|---|---|
| www.iraqfsc.iq / iraqfsc.iq | Federal Supreme Court decisions | Cloudflare "Just a moment..." challenge (403), robots.txt included. Not used. |
| parliament.iq | Council of Representatives (laws) | Cloudflare challenge (403). Not used. |
| www.hjc.iq, iraqld.hjc.iq | Supreme Judicial Council, Iraqi Legal Database | "Attention Required! \| Cloudflare" (403). Not used. |
| sjc.iq | Supreme Judicial Council | 403 page. Not used. |
| iraqld.e-sjc-services.iq -> iraqld.msla.iq | Iraqi Legal Database (new host) | robots.txt 200 (Cloudflare managed, content signals); home page 403 "تم منع هذا الطلب — مسلة" WAF block. Not used. |
| moj.gov.iq, www.moj.gov.iq | MoJ / Al-Waqai Al-Iraqiya gazette | Connect timeout (https and http). Not used. |
| mojsc.gov.iq, iraqld.iq, ar.parliament.iq | guesses | DNS does not resolve. |
| legislation.krd | Kurdistan Parliament legislation database | robots.txt 404 (none); no terms/copyright page; no challenge. **Used** (legislation). |
| www.parliament.krd | Kurdistan Parliament | robots.txt 404; only stated licence is CC BY 4.0 for *photographs* (/english/get-involved/photo-copyrights/). Links to legislation.krd. |

No federal case law or federal legislation source is reachable without a bot challenge/WAF.
No Kurdistan Region court decisions site found.
