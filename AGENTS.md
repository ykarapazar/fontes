# Notes for coding agents

Fontes is an MCP server: seven read-only tools that fetch case law and legislation live from
official sources, one adapter per jurisdiction. The package is `fontes-mcp`, the import name is
`world_legal_mcp`, the console script is `fontes`.

## Layout

- `src/world_legal_mcp/jurisdictions/<code>.py`: one adapter per jurisdiction, auto-discovered.
  The contract is [docs/ADAPTER_SPEC.md](docs/ADAPTER_SPEC.md). Adapters return records from
  `models.py`; `render.py` turns them into markdown; `server.py` defines the tools.
- `_http.py`: the only way to reach a source (own User-Agent, per-host throttle, TLS bundle).
- `installer/`: macOS, Windows and `.mcpb` installers. `relay/`: the opt-in usage-count relay.
- `scripts/`: generators and checks, run by hand or by `.github/workflows/`.

## Tests

```bash
uv run pytest -q tests --ignore=tests/live      # offline; what CI runs before a release
uv run pytest tests/live -k "test_nl or [nl]"   # one jurisdiction against the real source
```

Live tests call government websites: run them for the adapters you touched, not the whole
folder. A live failure can be the source changing; check it with the code from before your change.

## Generated files: change the generator, then rerun it

| file | generator |
|---|---|
| README.md blocks `coverage`, `sources` (also in translated READMEs) | `scripts/readme_tables.py` |
| README.md block `map`, `docs/assets/coverage-map*.svg` | `scripts/coverage_map.py` |
| README.md block `languages` (also in docs/index.html, translations) | `scripts/i18n_docs.py` |
| `docs/COVERAGE.md`, `docs/i18n/*/COVERAGE.md` | `scripts/catalogue.py` |
| `plugin/`, `.claude-plugin/marketplace.json`, versions in `server.json` | `scripts/plugin_bundle.py` |
| `docs/HEALTH.md`, `docs/status/`, `research/health/*.json` | `health.yml` (daily, commits to main) |
| `research/languages.json` | `scripts/languages.py` |

The version lives in `pyproject.toml`; `uv run python scripts/plugin_bundle.py` copies it on.

## Translations

`docs/i18n/<lang>/` holds translations of README, INSTALL, PRIVACY, FAQ, KEYS and index.html;
`installer/locales/` holds the installer strings. When an English fact changes (a command, a
version, a file name), change it in the translations too. Rules: [docs/i18n/TRANSLATING.md](docs/i18n/TRANSLATING.md).
`uv run python scripts/i18n_check.py` checks them.

## Rules

- Official or public-body sources only. Respect robots.txt and each source's terms; never invent
  identifiers. A source that needs permission gets `needs_permission=True` (see ADAPTER_SPEC).
- Don't push to `main` or publish a release without the maintainer.
