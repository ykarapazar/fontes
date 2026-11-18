"""Write the Claude plugin bundle (plugin/) and the repo's marketplace file from the code.

    uv run python scripts/plugin_bundle.py          # write
    uv run python scripts/plugin_bundle.py --check  # exit 1 if a file is out of date

The plugin runs `uvx fontes-mcp==<pyproject version>` (Anthropic's directory needs a pinned
launcher) and its README lists every host Fontes can contact, read from the adapters' source.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src/world_legal_mcp"
OUT = ROOT / "plugin"
REPO = "https://github.com/ykarapazar/fontes"
FACTS = json.loads((ROOT / "installer/mcpb/manifest.json").read_text())

URL = re.compile(r"https?://([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
HOST_CONST = re.compile(r'^[A-Z_]*HOST[A-Z_]* *= *"(?:https?://)?([A-Za-z0-9.-]+)', re.M)
OWN = {"pypi.org": "the daily version check (off: `FONTES_NO_UPDATE_CHECK=1`)",
       "relay.kinetra.fit": "bug reports you confirm, and usage counts only if you set `FONTES_STATS=1`",
       "github.com": "links to the Fontes repository in messages; nothing is sent"}


def version() -> str:
    return re.search(r'^version = "(.+)"', (ROOT / "pyproject.toml").read_text(), re.M)[1]


def source_hosts() -> list[str]:
    hosts = set()
    for f in sorted((SRC / "jurisdictions").glob("*.py")):
        text = f.read_text()
        hosts |= {h.lower() for h in URL.findall(text) + HOST_CONST.findall(text)}
    return sorted(h for h in hosts if "." in h and h not in OWN and not h.endswith((".py", ".json")))


def files() -> dict[Path, str]:
    ver = version()
    user_config = {k: {kk: vv for kk, vv in v.items() if kk != "default"}
                   for k, v in FACTS["user_config"].items()}
    env = FACTS["server"]["mcp_config"]["env"]
    plugin = {
        "name": "fontes",
        "displayName": "Fontes",
        "version": ver,
        "description": FACTS["description"],
        "author": FACTS["author"],
        "homepage": "https://ykarapazar.github.io/fontes/",
        "repository": REPO,
        "license": "Apache-2.0",
        "keywords": FACTS["keywords"],
        "icon": "./icon.png",
        "documentationUrl": f"{REPO}#readme",
        "supportUrl": f"{REPO}/issues",
        "privacyPolicyUrl": f"{REPO}/blob/main/docs/PRIVACY.md",
        "userConfig": user_config,
    }
    mcp = {"mcpServers": {"fontes": {"command": "uvx", "args": [f"fontes-mcp=={ver}"], "env": env}}}
    market = {
        "name": "fontes-legal",
        "owner": {"name": FACTS["author"]["name"]},
        "description": "Fontes: live case law and legislation from official sources.",
        "plugins": [{"name": "fontes", "source": "./plugin", "description": FACTS["description"],
                     "category": "research"}],
    }
    hosts = source_hosts()
    own = "\n".join(f"- `{h}`: {why}" for h, why in OWN.items())
    readme = f"""# Fontes plugin

{FACTS["long_description"].split(" This extension")[0]} It is a research tool, not legal advice.

This plugin adds the Fontes MCP server to Claude. It runs on your computer with
`uvx fontes-mcp=={ver}` (needs [uv](https://docs.astral.sh/uv/)): no account and no hosted
service. Source code, licence (Apache 2.0) and full documentation: {REPO}

Install in Claude Code:

    /plugin install fontes --marketplace ykarapazar/fontes

## Tools

{chr(10).join(f"- `{t['name']}`: {t['description']}" for t in FACTS["tools"])}

All tools only read. Nothing is written outside Fontes's own cache folder (the daily update
check and, if you opt in, usage counts).

## Settings

All optional, all stored as secrets: a PISTE client ID and secret turn France on; an
api.data.gov key lifts the United States search limit. How to get them:
{REPO}/blob/main/docs/KEYS.md. They are sent only to the French and US government APIs.

## What it sends, and where

When you ask a question, Fontes sends your search terms or document id to the court or
government website of the jurisdiction you asked about, and nowhere else. It identifies itself
with a `Fontes/<version>` User-Agent that names the repository and a contact address. Besides those sources it contacts only:

{own}

Privacy notice: {REPO}/blob/main/docs/PRIVACY.md

### Every source host in the code ({len(hosts)})

Generated from the adapters' source by `scripts/plugin_bundle.py`: every host an adapter
fetches from or links to. A host is contacted only when you ask about its jurisdiction.

{chr(10).join(f"- `{h}`" for h in hosts)}
"""
    return {
        OUT / ".claude-plugin/plugin.json": json.dumps(plugin, indent=2, ensure_ascii=False) + "\n",
        OUT / ".mcp.json": json.dumps(mcp, indent=2) + "\n",
        OUT / "README.md": readme,
        ROOT / ".claude-plugin/marketplace.json": json.dumps(market, indent=2, ensure_ascii=False) + "\n",
    }


def main() -> int:
    stale = [p for p, text in files().items() if not p.exists() or p.read_text() != text]
    if "--check" in sys.argv:
        for p in stale:
            print(f"out of date: {p.relative_to(ROOT)}")
        return 1 if stale else 0
    for p, text in files().items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    shutil.copyfile(ROOT / "docs/assets/brand/mark-512.png", OUT / "icon.png")
    print(f"wrote {len(files())} files; {len(source_hosts())} source hosts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
