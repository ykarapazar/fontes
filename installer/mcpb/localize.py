"""Add MCPB localisation to a built manifest: one mcpb-resources/<lang>.json per locale file.

    python3 localize.py <manifest.json> <locales dir> <out dir>

Each resource file holds only the translated fields (description, long_description, keywords,
tool descriptions) in manifest shape; display_name stays "Fontes". English stays in the
manifest itself. Unverified: whether Claude Desktop asks for "tr" or "tr-TR" (see
research/languages.md); files are named by our locale codes.
"""
import json
import sys
from pathlib import Path

manifest_path, locales, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
en = json.loads((locales / "en.json").read_text(encoding="utf-8"))
out.mkdir(parents=True, exist_ok=True)
for f in sorted(locales.glob("*.json")):
    if f.stem == "en":
        continue
    s = {**en, **json.loads(f.read_text(encoding="utf-8"))}
    res = {"description": s["mcpb_description"], "long_description": s["mcpb_long_description"],
           "keywords": [k.strip() for k in s["mcpb_keywords"].split(",") if k.strip()],
           "tools": [{"name": t["name"], "description": s.get(f"mcpb_tool_{t['name']}", t["description"])}
                     for t in manifest["tools"]]}
    (out / f"{f.stem}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
manifest["localization"] = {"resources": f"{out.name}/${{locale}}.json", "default_locale": "en"}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
