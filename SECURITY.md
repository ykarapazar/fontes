# Security policy

## Reporting a problem

Please report security problems **privately** by email to **fontesmcp@proton.me**. Do not open a
public issue for them.

Include what you found, how to reproduce it, and the Fontes version if you know it. You will get
a reply; Fontes is maintained by one person, so please allow a few days. Once a fix is released,
the problem is described in [CHANGELOG.md](CHANGELOG.md), with credit to you if you want it.

## Supported versions

Only the latest release gets fixes. The installer and the `.mcpb` bundle update themselves once
a day. If you run `uvx fontes-mcp` yourself, `uvx fontes-mcp@latest` gets the newest release.

## What is in scope

- The Fontes server (`src/`), the installer and launcher (`installer/`), and the report relay
  (`relay/`).
- Examples: a way to make Fontes send data somewhere other than the source being searched, the
  PyPI update check or the opt-in relay; leaks of search terms or ids into bug reports or usage
  counts; the installer changing more than its own entry in the app settings.

Problems in the court and government websites that Fontes reads are out of scope; please report
those to the publisher.
