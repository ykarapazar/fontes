# ADGM Courts (adgm): source check, 2026-11-06

No adapter built. ADGM's Terms of Use forbid automated querying and scraping of all ADGM
platforms, and they name the corporate website (Courts judgments), E-courts and the Thomson
Reuters legislation site as covered. Checked from a UK IP with the project User-Agent.

## Terms of Use (www.adgm.com/information/terms-and-conditions, last updated 29/09/2026)
- 2.1: the terms apply to all ADGM Platforms unless separate, platform-specific terms exist,
  including: Registry 2.0, AccessADGM, AccessRP, FSRAConnect, EPRS, Market Disclosure,
  **E-courts**, **Corporate Website**, Fusion Supplier Lifecycle Management, **Thomson Reuters**.
- 8.1: licence to "access, view, use and display the Platforms and the Services on your devices
  for your personal purposes only or, if you are using the Platforms on behalf of a Corporate
  User, the ordinary internal business of the Corporate User".
- 8.3, "you agree that you shall not": "conduct or facilitate any text mining, data mining, web
  scraping, screen scraping, data harvesting, data extraction, automated querying, crawling,
  spidering or any other analogous data collection or extraction techniques, whether manual or
  automated, in relation to the whole or any part of the Platform, the Services, or any Content;"
  The same list forbids making Content available "to any person without our prior written
  consent".
- 11.1: all IP and database rights reserved to ADGM.
- No platform-specific terms were found for the Courts judgments page (it links no other terms).
- Result: this is an outright prohibition, not a "with permission" clause. An MCP server that
  queries the judgments list and fetches PDFs on demand is "automated querying" / "data
  extraction". Under the project rule, this source is not used.

## Hosts
- www.adgm.com: robots.txt allows `/` and disallows /episerver, /util, /mediacentre/,
  /media-center/, /doing-business/, /adgm-academy/, /api/. `/adgm-courts/judgments` → 200,
  server-rendered HTML; judgments link to PDFs at
  `assets.adgm.com/download/assets/<case no., e.g. ADGMCFI-2022-111>/<hash>`.
  Robots allows it; the terms do not.
- assets.adgm.com: robots.txt 404.
- en.adgm.thomsonreuters.com (ADGM legislation and rulebooks): 403 to this client, including
  robots.txt. It is a named Platform under 2.1 anyway.
- www.adgmcourts.com: 403 to this client.

## If ADGM ever grants written permission
Case law would be easy: an HTML listing → sealed text-layer PDFs (`_http.pdf_text`), with case
numbers like ADGMCFI-2022-111 as ids. Build it gated (`needs_permission=True`) like difc.py.
Legislation would also need the Thomson Reuters host to stop returning 403.
