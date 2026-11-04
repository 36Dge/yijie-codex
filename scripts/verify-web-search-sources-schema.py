#!/usr/bin/env python3
"""Require canonical source metadata to be the only input-only schema extension."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
old = root / ".yijie/schemas/input-only-app-server/generated-json-schema"
new = Path(sys.argv[1])
source_types = {"WebSearchSource", "ResponsesApiWebSearchSource"}


def without_source_extension(value):
    if isinstance(value, list):
        return [without_source_extension(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, child in value.items():
        # The aggregate canonical file namespaces its definitions under v2.
        if key in ("definitions", "$defs", "schemas", "v2"):
            child = {k: v for k, v in child.items() if k not in source_types}
        if key == "properties" and "sources" in child:
            # Strip only our typed optional source list, never arbitrary fields.
            field = json.dumps(child["sources"])
            if "WebSearchSource" in field:
                child = {k: v for k, v in child.items() if k != "sources"}
        result[key] = without_source_extension(child)
    return result


before = {p.relative_to(old).as_posix(): json.loads(p.read_text()) for p in old.rglob("*.json")}
after = {p.relative_to(new).as_posix(): json.loads(p.read_text()) for p in new.rglob("*.json")}
extra = set(after) - set(before)
if any(Path(name).stem not in source_types for name in extra) or set(before) - set(after):
    raise SystemExit("Unexpected canonical schema file change")
changed = []
for name, value in before.items():
    if without_source_extension(after[name]) != value:
        raise SystemExit("Non-source canonical schema change: " + name)
    if after[name] != value:
        changed.append(name)
if not changed:
    raise SystemExit("Source schema extension is missing")
print("Canonical optional search sources only:", len(changed), "changed files;", len(extra), "new type files")
