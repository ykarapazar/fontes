# Qatar (qa): source check, 2026-11-06

No adapter built: every official source that has the texts needs prior written permission
for the reuse an MCP server makes. Checked from a UK IP with the project User-Agent.

## Al Meezan (almeezan.qa), Ministry of Justice: legislation + Court of Cassation rulings
- React SPA. API base from the bundle (`VITE_API_BASE_URL`): `https://api.moj.gov.qa/api/v1`,
  `?lang=1` (en) / `2` (ar) appended to every call. Public reads need no token; reCAPTCHA v3
  and login apply only to the account/e-services flows.
- Endpoints seen in the bundle (not called, apart from the CMS):
  `GET /Legislation/search-index?…&showAlmeezan=true`, `GET /legislations/{id}`,
  `GET /Legislation/{id}/almawad-lookup`, `GET /Legislation/{id}/files/{fileId}/download`,
  `GET /Ruling/search-index?…` (filters: courts, court-circuits, litigation-levels, subjects,
  years), `GET /rulings/{id}`, lookups `/Ruling/courts|years|subjects`.
  SPA routes: `/legislations/{type}/{year}/{number}/general`, `/rulings/{id}`.
- robots.txt (almeezan.qa): `User-agent: * / Allow: /`. api.moj.gov.qa/robots.txt: 404.
- Terms of Use (CMS StaticContents key `Terms_of_Use`, published 2026-03-30):
  "All content on this website, including text, graphics, logos, and design, is owned by the
  Ministry of Justice unless otherwise stated. No content may be copied, reproduced,
  distributed, or used without prior written permission."
  Website Usage Guidelines: "Users may not reproduce, distribute, or reuse content without
  prior permission."
  → PERMISSION NEEDED (Ministry of Justice). The same MoJ backend serves
  officialgazette.gov.qa, so the Official Gazette is covered by the same terms.

## Qatar International Court (www.qicdrc.gov.qa): English judgments
- Drupal; listing `/judgments`, judgment pages `/judgments/<slug>` (e.g. `ctfic00112026`).
- robots.txt: `Crawl-delay: 10`; explicitly allows GPTBot, ClaudeBot, Claude-User,
  PerplexityBot, CCBot etc. ("being cited by ChatGPT, Perplexity, Claude ... is the point").
- Terms (on /privacy-policy-data-protection, "COPYRIGHT" 5(c)): "any material on the site may
  not be copied, displayed, distributed, downloaded, licensed, modified, published, re-posted,
  reproduced, reused, sold, transmitted, used to create a derivative work or otherwise used for
  public or commercial purposes in whole or in part without prior written permission from the
  QICDRC". Personal / in-firm use only (4).
  → PERMISSION NEEDED (QICDRC). The robots.txt AI allowance is a strong sign they would agree.

## Others
- Supreme Judicial Council (www.sjc.gov.qa): SharePoint; its `_api/web/lists/...` REST calls
  redirect a non-browser client to `/ar/Pages/Error.aspx`. No usable route without faking a browser.
- QFC Authority (www.qfc.qa, QFC laws and regulations): robots.txt only disallows /umbraco/,
  but Terms of Use: "You must not reproduce or store any part of this site on any other website
  or include it in any public or private electronic retrieval system or service, without the
  QFCA's prior written permission". → blocked.

## If permission is granted
Al Meezan alone gives legislation (article-level via almawad) and Cassation rulings, through a
plain JSON API: build it with `needs_permission=True` like bh.py. QICDRC adds English case law
(HTML pages, 10 s crawl delay).
