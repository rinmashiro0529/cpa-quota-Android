#!/usr/bin/env python3
"""Refresh content hashes after an intentional, reviewed proposal edit."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "plan-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
features = json.loads((ROOT / "manifests/feature-parity.json").read_text(encoding="utf-8"))["features"]
tasks = json.loads((ROOT / "manifests/work-items.json").read_text(encoding="utf-8"))["work_items"]
manifest["counts"] = {
    "features_total": len(features),
    "features_required": sum(x["release_required"] for x in features),
    "features_optional": sum(not x["release_required"] for x in features),
    "tasks_total": len(tasks),
    "tasks_required": sum(x["release_required"] for x in tasks),
    "tasks_optional": sum(not x["release_required"] for x in tasks),
}
entries = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path == manifest_path or "__pycache__" in path.parts:
        continue
    data = path.read_bytes()
    entries.append({
        "path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "git_blob_sha": hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    })
manifest["files"] = entries
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Updated integrity entries for {len(entries)} files; manifest is covered by its Git commit, not a self hash.")

