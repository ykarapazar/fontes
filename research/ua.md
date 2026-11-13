# Ukraine (`ua`): not built (checked 2026-11-05, UK IP)

No adapter. Every official route is either forbidden for automated use, bulk-only, or unreachable.

## Case law
- **Unified State Register of Court Decisions** (`reyestr.court.gov.ua`, State Judicial Administration).
  - robots.txt: none (HTTP 404).
  - Terms (`/Rules`, "Правила роботи з Єдиним державним реєстром судових рішень") **forbid** "здійснювати
    автоматичні або автоматизовані запити на пошук та копіювання ("викачування") БД" (making automatic
    or automated requests to search and copy the database). They cite Section XVI of the Criminal Code
    (computer crimes). They also forbid building search or meta-search systems on the DB for commercial
    purposes, and mirrors. Per-IP page limits apply, and repeated overload leads to a long ban.
  - The search page carries a captcha modal ("interactive protection element") whose stated purpose is to
    stop automated search requests.
  - No search POST was sent: the terms rule it out.
  - Decision texts are official documents, which the copyright clause excludes. The prohibition
    covers the automated access itself.
  - Verdict: outright forbidden, so not built. A route would need written permission from the State
    Judicial Administration.
- **data.gov.ua bulk export** (dataset `16ab7f06-7414-405f-8354-0a492475272d`, CC-BY). The CKAN API only lists
  yearly ZIPs (`edrsr_data_2026.zip`, 338 MB). No datastore or per-record API. It is bulk only, which the project rules exclude.
  - data.gov.ua robots.txt carries Cloudflare content signals.
- **Constitutional Court** (`ccu.gov.ua`). robots.txt has `Crawl-delay: 10` and disallows `/search/`,
  `/docs-search` and every `?page=` listing. Decision pages `/dokument/{slug}` are allowed, but there is no
  permitted search route, so search_caselaw can't be built.
- `lpvs.court.gov.ua` (Supreme Court legal-positions DB) does not resolve.

## Legislation
- `zakon.rada.gov.ua` and `data.rada.gov.ua` (Verkhovna Rada) **time out** from the UK. Tried twice each (https and http,
  `/robots.txt`, `/laws/show/435-15`, `/ogd/zak/laws/`). robots.txt and terms are unknown because they are unreachable.
  - Known but unverified: the open-data API needs a free token.
  - Would need an egress point in Ukraine or the EU.
