# Adapter spec: adding a country

One country = one file, `src/world_legal_mcp/jurisdictions/<code>.py`, plus its live test.
Read this, then `base.py` and `models.py`. They are short and they are the contract.

## What you build

A `Jurisdiction` subclass that returns **records from `models.py`**, never markdown. The
server renders every country the same way, pages long texts, caches them and filters
TOCs by keyword. You only fetch, parse and clean.

| Method | Returns | Notes |
|---|---|---|
| `search_caselaw(query, *, limit, page, filters)` | `Results` of `DecisionHit` | `page` is 1-based. Respect `limit`. |
| `get_decision(id)` | `Decision` | Full text, untruncated. |
| `search_legislation(query, *, limit, page, filters)` | `Results` of `LawHit` | |
| `get_legislation_toc(id)` | `Toc` | Every entry a reader could open has `provision` set. |
| `get_legislation_provision(id, provision)` | `Provision` | Accept the labels your TOC shows, plus obvious variants ("Madde 5", "5", "art. 5"). |
| `get_legislation_text(id)` | `LawText` | Full consolidated text. |

Implement only what the source supports. A missing method = "not supported", and the
server tells the user where to look instead. The world map counts a country as having
**case law** when `search_caselaw` + `get_decision` exist, and **legislation** when
`search_legislation` + `get_legislation_provision` exist.

## Field rules (the conformance test checks these)

- `id` is the source's own identifier (ECLI, neutral citation, documentId, law number…).
  Never invent one. It must round-trip: an id from a search works in the get method.
- `url` is a public page a human can open to check the original.
- Dates are `YYYY-MM-DD`, or `""` when the source has none.
- Text is clean markdown: no HTML tags, collapsed whitespace, paragraph breaks kept.
  Use `markdownify` for HTML bodies. Do not translate.
- Titles: case name if the source has one, else `"<court> <case number>"`.
- `Results.total` is the source's hit count, or `None` if it does not say.
- `Results.note`: one line the user must know (e.g. "data lags about 5 months").

## Errors

Raise, don't return text:

- `NotFound`: id or provision doesn't exist.
- `BadRequest`: bad id format or filter value. Say what a good one looks like.
- `SourceError(msg, status)`: HTTP error, block page or unexpected payload.

`httpx` network errors may propagate; the server handles them.

## HTTP and rate limits

- Use `_http.get` / `_http.post` only. They add the project's own User-Agent (never fake a browser), the per-host
  throttle, one retry on 429/503 with Retry-After, and per-host counters.
- Set `min_interval = {host: seconds}` to stay under the source's limit. Unknown limit:
  start at 1.0 s.
- Fill `Source.rate_limit` with what you know **and how you know it**: "documented: 60/min",
  "~10 req/30 s per IP, 429 + Retry-After (measured 2026-11)", or "unknown; 1 s spacing,
  no 429 seen in N requests (2026-11)". The conformance run prints per-host counts to help.
- Never hammer a source to find its limit. A handful of requests is enough.

## Source terms (needed before anything is hosted)

For each `Source` set: `covers`, `licence`, `commercial_use` (True/False/None = unknown),
`ai_use` (False if robots.txt or terms opt out of AI/TDM use), `auth`, `terms_url`.
Check robots.txt and the terms page. Do not guess; `None` plus a line in your report is
fine.

If a source's terms or robots.txt forbid automated use without permission, do not build
on it. Set `warning` only for lighter limits that still allow on-demand automated reading
(non-commercial only, attribution, unofficial text): one plain sentence, shown on every
response from that source and in `list_jurisdictions`.

Existing adapters for sources that need permission set `needs_permission=True` (with a
`warning`). The server never calls such a source unless the operator lists the code in
`WLM_PERMITTED` (e.g. `WLM_PERMITTED=in,de`), and their live tests skip likewise. The server refuses a call outright only when every source of that kind (case law or
legislation) is gated. If an adapter has an open source next to a gated one of the same
kind, the adapter must skip the gated source itself unless `j.code in permitted_codes()`.

## Hard rules

- Official or public-body sources only. No commercial databases.
- Do not scrape anything robots.txt or the terms forbid. If the only route is forbidden,
  leave that method out and report it.
- No API keys in code. Sources that need a free key: read it from an env var
  `WLM_<CODE>_<NAME>_KEY`, and say "needs free key" in `auth`. Skip paid ones.
- No headless browsers, no OCR, no bulk download, no disk cache.
- Touch only your own files: `jurisdictions/<code>.py`, `tests/live/test_<code>.py`,
  and optionally `research/<code>.md`. **Do not edit** `base.py`, `models.py`,
  `render.py`, `server.py`, `_http.py` or `registry.py`. If the contract can't express
  your source, stop and report what is missing.
- Shared helpers already in `_http`: `clean` (one-line whitespace cleanup),
  `html_to_md` / `html_paragraphs` (HTML to clean markdown, layout tables flattened),
  `iso_date` (day-first or ISO dates to `YYYY-MM-DD`), `en_date` ('July 8, 2016' to
  `YYYY-MM-DD`), `pdf_text` (text-layer PDF to cleaned lines, pages split by a blank line), `lru_put` (small bounded in-memory
  cache), `text` / `localname` (lxml), `today` (ISO date for "as of"), `get_or_raise` (GET with
  404 → NotFound), `check_date` / `require_iso` (reject non-`YYYY-MM-DD` input), `article_key`
  (Spanish 'Artículo 5 bis' → '5 bis'), `fold_marks` / `fold_combining` / `fold_ascii` /
  `fold_ascii_ws` (accent folding). Use them instead of writing your own.
- Anything else you need goes in your own file. Note it in your report so it can be
  promoted later.

## Samples and tests

Set `samples` on the class: `caselaw_query`, `decision_id`, `legislation_query`, `law_id`,
`provision`, using stable, well-known items (a supreme-court decision, the civil code).

When a jurisdiction has several sources of the same kind (e.g. two case-law sources picked by a
`court` filter), give each one a `probe` on its `Source`: the same keys, plus `filters` for the
search, e.g. `probe={"caselaw_query": "ihale", "filters": {"court": "sayistay_daire"}}`.
`scripts/health.py` uses it to check that source on its own (docs/HEALTH.md).

Must pass:

```
uv run pytest tests/test_registry.py -q
uv run pytest tests/live/test_conformance.py -k "[<code>]" -s   # brackets: plain -k es would match every test
```

Also add `tests/live/test_<code>.py` with 2–4 checks of country-specific behaviour
(filters, id variants, provision label variants), going through `server.*` tools so the
rendered output is tested too.

## Report back

1. What works (case law / legislation), with the conformance output.
2. Each source: licence, commercial use, AI opt-out, auth, rate limit (and how you know).
3. What is missing or blocked, and why.
4. Data quirks the user should know (lag, coverage years, anonymisation).
