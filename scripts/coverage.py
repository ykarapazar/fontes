"""Print coverage.json for the world map: one entry per adapter.

    uv run python scripts/coverage.py > coverage.json
"""
import json

from world_legal_mcp import registry

registry.discover()
out = []
for j in registry.available():
    cov = j.coverage()
    out.append({
        "code": j.code,
        "name": j.name,
        "caselaw": cov["caselaw"],
        "legislation": cov["legislation"],
        "sources": [{"name": s.name, "covers": list(s.covers), "licence": s.licence,
                     "commercial_use": s.commercial_use, "ai_use": s.ai_use,
                     "auth": s.auth, "rate_limit": s.rate_limit} for s in j.sources],
    })
print(json.dumps(out, ensure_ascii=False, indent=2))
