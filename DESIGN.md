# world-legal-mcp — design

Goal: live case law (precedent) and legislation for as many jurisdictions as have open sources,
behind ONE small, stable set of MCP tools. Made to be easy for lawyers to install.

## Principles (inherited from nl-legal-mcp / uk-legal-mcp)
- Fetch live from official sources at call time. No bulk indexing, no disk cache (an in-process
  LRU for big parsed documents is fine).
- Respect each source's terms. No scraping where it is forbidden (e.g. BAILII). Throttle per host.
- Identifiers come from the source, never invented. Every result carries the source URL so a
  lawyer can check the original.
- Output is markdown, sized for an LLM context (max_chars + offset paging on long documents).

## Both shapes from one codebase
1. **Unified server** `world-legal-mcp`: one fixed tool set; the jurisdiction is a parameter. The
   tool count does not grow with countries, which keeps the model's context small.
2. **Per-country server**: the same binary filtered to one jurisdiction
   (`world-legal-mcp --only nl`) plus thin console-script aliases (`nl-legal-mcp`, `uk-legal-mcp`)
   so existing installs keep working.

## Unified tools
| Tool | Purpose |
|---|---|
| `list_jurisdictions(query?)` | Codes, names, sources, what each supports, and each adapter's extra filters. |
| `search_caselaw(jurisdiction, query, limit=10, page=1, filters={})` | Full-text search of decisions. |
| `get_decision(jurisdiction, id, max_chars=60000, offset=0)` | One decision as markdown (ECLI, neutral citation, slug, ...). |
| `search_legislation(jurisdiction, query, limit=20, page=1, filters={})` | Find laws/acts. |
| `get_legislation_toc(jurisdiction, id, keyword?)` | Structure of an act. |
| `get_legislation_provision(jurisdiction, id, provision)` | One article/section. |
| `get_legislation_text(jurisdiction, id, max_chars=60000, offset=0)` | Full consolidated text. |

Jurisdiction codes: ISO 3166-1 alpha-2 lower-case (`nl`, `gb`, `tr`, `de`), sub-national as
`us-ca`, `au-nsw`; supranational/international as `eu`, `echr`, `icj`, ... Aliases accepted
(`uk` -> `gb`).

## Adapter contract
`src/world_legal_mcp/jurisdictions/<code>.py` defines a `Jurisdiction` subclass:
- metadata: `code`, `name`, `languages`, `sources` (name + URL + licence note), `aliases`
- `caselaw_filters` / `legislation_filters`: documented extra filters (name -> description)
- optional async methods: `search_caselaw`, `get_decision`, `search_legislation`,
  `get_legislation_toc`, `get_legislation_provision`, `get_legislation_text`.
  A missing method means "not supported" and the unified tool says so clearly, pointing to the
  official site.
- adapters return markdown strings (same style as the NL/UK servers).

A registry auto-discovers adapters. Shared HTTP layer: one httpx client, browser UA, per-host
throttle (each adapter declares its min interval), consistent error messages.

## Shipping to lawyers (later phases)
1. `uvx world-legal-mcp` (PyPI).
2. One-click Claude Desktop extension (.mcpb).
3. Hosted remote MCP URL (streamable HTTP) that can be pasted into Claude / ChatGPT connectors,
   with no install at all.
4. Simple landing page and README with copy-paste setup.

## Tests
`tests/live/` smoke-tests every adapter against the real sources (one search plus one fetch each).
Run per jurisdiction: `uv run pytest tests/live -k nl`.
