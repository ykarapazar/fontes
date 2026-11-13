# Malaysia (`my`): checked 2026-11-06, no adapter built

Both official sources were checked live. Neither can be used under the project rules
(official sources only, honour robots.txt and terms, no circumventing access controls).
So there is no `jurisdictions/my.py`.

## Legislation: Laws of Malaysia (lom.agc.gov.my, Attorney General's Chambers)

- robots.txt: `https://lom.agc.gov.my/robots.txt` returned **HTTP 500** on 3 tries (2026-11-06).
  RFC 9309 §2.3.1.4 says an unreachable robots.txt (5xx) means the crawler must assume
  complete disallow. The parent site `https://www.agc.gov.my/robots.txt` reads
  `User-agent: * / Disallow: /`.
- Terms (`tnc.php`) say nothing about automated access. Clause 5: "Copyright 2023 by
  Attorney General's Chambers, Malaysia, all rights reserved." Clause 9: "The federal
  legislation can be accessed and downloaded at no charge from this portal". Clause 10:
  a print-out is not a copy of the Gazette.
- Technical access controls (new since `my-eli-mcp` was written):
  - Search (`search.php` → `fess-proxy.php`) and every listing (`principal.php`,
    `subsid.php`, …) return **AES-256-GCM-encrypted JSON**. The page decrypts it in the
    browser (`js/responseCrypto.js`, key embedded as `SEARCH_RESPONSE_KEY`). The old
    plain endpoint (`json-updated-2024.php`) is commented out.
  - Act pages need an HMAC-signed token: `act-detail.php?language=BI&act=136` returns
    `Invalid request`. Signed links only come from `processFile.php?isDirect=1&token=…`
    (base64 of `url|sha256-hmac`) on server-rendered pages.
  - PDFs sit at `/ilims/upload/portal/akta/outputaktap/<internal id>_BI/<TITLE>.pdf`.
    The internal id can only be found through the encrypted listings or signed pages.
- Verdict: blocked. Building it would mean decrypting responses that were encrypted on
  purpose, on a host whose robots.txt is unreachable (so the RFC says assume disallow).

## Case law: Office of the Chief Registrar, Federal Court (kehakiman.gov.my)

- The judgment portal is `https://ejudgment.kehakiman.gov.my/EJudgmentWeb/SearchPage.aspx`,
  not efs. It has a plain JSON service, `eJudgmentService.asmx/GetEJudgmentPortalSearchList`
  (POST `{"Param":{…,"Search":"contract","CurrPage":1,"Ordering":"DATE_OF_AP_DESC"}}`,
  20 per page, `TOTAL_RECORD` given, headnote keywords + parties + judge + DocumentID).
  ejudgment has no robots.txt (404).
- Full texts are served only from
  `https://efs.kehakiman.gov.my/EFSWeb/DocDownloader.aspx?DocumentID=<guid>&Inline=true`.
  `https://efs.kehakiman.gov.my/robots.txt`: `User-agent: * / Disallow: /efsweb/docdownloader.aspx`
  and `Disallow: /efsweb/efiling/`. The server is IIS, which ignores case, so this covers the path.
- Terms, `https://www.kehakiman.gov.my/en/copyright` (the BM page `/ms/hakcipta` has the same
  English text): "No part or parts of this portal may be modified, copied, distributed,
  retransmitted, broadcast, displayed, reproduced, published, licensed, transferred, sold or
  commercially dealt with in any manner without the express prior written consent of Chief
  Registrar's Office Federal Court of Malaysia."
- kehakiman.gov.my robots.txt is the Drupal default (disallows `/search/`, admin and user paths).
- Verdict: blocked. Full texts are robots-disallowed, and the copyright terms require written
  consent before anything is copied or retransmitted.

## What would unlock it
- Case law: written consent from the Chief Registrar's Office (contact page on
  kehakiman.gov.my), covering automated retrieval from ejudgment and DocDownloader.
- Legislation: written permission from AGC (lom.agc.gov.my `contact.php`), ideally with a
  plain (unencrypted) endpoint, or a fixed robots.txt that allows access.
