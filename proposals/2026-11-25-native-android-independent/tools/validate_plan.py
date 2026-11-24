#!/usr/bin/env python3
"""Validate this proposal's structure and traceability; never runs app tests."""
from pathlib import Path
from urllib.parse import unquote
from collections import Counter
import hashlib
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PLAN_ID = "native-android-independent-20261125"
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

def read(path):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"{path}: {exc}")
        return {}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def candidate_files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts
                  and p.name != "plan-manifest.json")

manifest = read("plan-manifest.json")
feature_doc = read("manifests/feature-parity.json")
task_doc = read("manifests/work-items.json")
source = read("manifests/source-baseline.json")
target = read("manifests/target-preservation.json")
evidence = read("manifests/evidence-template.json")

for name, obj in [("manifest", manifest), ("features", feature_doc),
                  ("tasks", task_doc), ("source", source), ("evidence", evidence)]:
    require(obj.get("plan_id") == PLAN_ID, f"{name}: wrong plan_id")
require(target.get("old_artifact_content_read") is False, "Isolation provenance changed")
require(target.get("isolated_path") == "proposals/2026-11-25-native-android-independent", "Wrong isolation path")
require(manifest.get("source_commit") == source.get("source_commit") == feature_doc.get("source_commit") == task_doc.get("source_commit"), "Source SHA mismatch")
require(re.fullmatch(r"[0-9a-f]{40}", source.get("source_commit", "")) is not None, "Invalid source SHA")
require(len(target.get("preserved_files", [])) == 9, "Unexpected target preservation count")

features = feature_doc.get("features", [])
tasks = task_doc.get("work_items", [])
fmap = {f["id"]: f for f in features}
tmap = {t["id"]: t for t in tasks}
require(len(fmap) == len(features), "Duplicate feature ID")
require(len(tmap) == len(tasks), "Duplicate task ID")
inventory = {x["path"] for x in source.get("source_inventory", [])}
allowed_states = set(task_doc.get("task_statuses", []))
required_features = {f["id"] for f in features if f["release_required"]}
required_tasks = {t["id"] for t in tasks if t["release_required"]}
require(len(required_features) == 93 and len(features) == 97, "Candidate scope count changed: review and version plan")
require(len(required_tasks) == 34 and len(tasks) == 38, "Candidate task count changed: review and version plan")

for f in features:
    fid = f["id"]
    require(bool(f.get("acceptance")), f"{fid}: missing acceptance")
    require(f.get("implementation_status") in allowed_states, f"{fid}: invalid state")
    require(bool(f.get("work_items")), f"{fid}: no task mapping")
    for path in f.get("source_paths", []):
        require(path in inventory, f"{fid}: source path absent from inventory: {path}")
    if f.get("requirement_kind") == "ios_parity":
        require(bool(f.get("source_paths")), f"{fid}: iOS parity without source")
    for tid in f.get("work_items", []):
        require(tid in tmap and fid in tmap[tid].get("feature_ids", []), f"{fid}/{tid}: asymmetric mapping")
    if f["release_required"]:
        implementation_tasks = set(f["work_items"]) - {"TASK-001", "TASK-033", "TASK-034"}
        require(bool(implementation_tasks & required_tasks), f"{fid}: covered only by review/optional tasks")
    if f.get("implementation_status") == "verified":
        require(bool(f.get("evidence")), f"{fid}: verified without evidence")

for t in tasks:
    tid = t["id"]
    require(re.fullmatch(r"TASK-\d{3}", tid) is not None, f"Invalid task ID: {tid}")
    require(t.get("repository") in {"rinmashiro0529/cpa-quota-Android", "rinmashiro0529/cpa-quota-ios"}, f"{tid}: wrong repository")
    require(t.get("milestone") in task_doc.get("milestones", {}), f"{tid}: unknown milestone")
    require(t.get("status") in allowed_states, f"{tid}: invalid state")
    require(bool(t.get("deliverables")) and bool(t.get("acceptance")), f"{tid}: incomplete card")
    for dep in t.get("depends_on", []):
        require(dep in tmap and dep != tid, f"{tid}: invalid dependency {dep}")
        if t["release_required"] and dep in tmap:
            require(tmap[dep]["release_required"], f"{tid}: optional task became hidden blocker")
    for fid in t.get("feature_ids", []):
        require(fid in fmap and tid in fmap[fid]["work_items"], f"{tid}/{fid}: asymmetric mapping")
    if t.get("status") == "verified":
        require(bool(t.get("evidence")) and bool(t.get("owner")), f"{tid}: verified without owner/evidence")

visited, active = set(), set()
def visit(tid):
    if tid in active:
        errors.append(f"Dependency cycle at {tid}")
        return
    if tid in visited or tid not in tmap:
        return
    active.add(tid)
    for dep in tmap[tid].get("depends_on", []):
        visit(dep)
    active.remove(tid)
    visited.add(tid)
for tid in tmap:
    visit(tid)
require(set(tmap.get("TASK-033", {}).get("depends_on", [])) == required_tasks - {"TASK-033"}, "Final gate does not include all required tasks")
require(set(tmap.get("TASK-033", {}).get("feature_ids", [])) == required_features, "Final gate feature coverage incomplete")

# Check Markdown files locally; external links are evidence pointers, not live-network assertions.
link_count, markdown_count = 0, 0
for path in sorted(ROOT.rglob("*.md")):
    markdown_count += 1
    body = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    fenced = None
    prose = []
    for line in body.splitlines():
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            if fenced is None:
                fenced = marker
            elif marker[0] == fenced[0] and len(marker) >= len(fenced):
                fenced = None
            continue
        if fenced is None:
            prose.append(line)
    require(fenced is None, f"{rel}: unclosed code fence")
    text = "\n".join(prose)
    for match in re.finditer(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
        href = match.group(1).split(' "', 1)[0].strip("<>")
        if re.match(r"^[a-zA-Z][\w+.-]*:", href) or href.startswith("#"):
            continue
        link_count += 1
        target_path = (path.parent / unquote(href.split("#")[0])).resolve()
        require(target_path.is_relative_to(ROOT) and target_path.is_file(), f"{rel}: broken/escaping link {href}")
    defined = set(re.findall(r"^\[([SA]\d+)\]:", body, re.M))
    used = set(re.findall(r"\[([SA]\d+)\](?![(:])", text))
    require(used <= defined, f"{rel}: undefined source labels {sorted(used - defined)}")

spec = importlib.util.spec_from_file_location("plan_indexes", ROOT / "tools/render_indexes.py")
indexes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexes)
for name, content in indexes.outputs().items():
    require((ROOT / name).is_file() and (ROOT / name).read_text(encoding="utf-8") == content, f"{name}: generated index is stale")

entries = manifest.get("files", [])
paths = {x["path"] for x in entries}
actual = {p.relative_to(ROOT).as_posix() for p in candidate_files()}
require(len(paths) == len(entries), "Duplicate integrity entry")
require(paths == actual, f"Integrity file set differs: missing={sorted(actual-paths)}, extra={sorted(paths-actual)}")
for entry in entries:
    path = (ROOT / entry["path"]).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        errors.append(f"Integrity path invalid: {entry['path']}")
        continue
    data = path.read_bytes()
    require(entry["bytes"] == len(data) and entry["sha256"] == sha256(data) and entry["git_blob_sha"] == git_blob(data), f"Integrity mismatch: {entry['path']}")

computed = {
    "features_total": len(features), "features_required": len(required_features),
    "features_optional": len(features) - len(required_features),
    "tasks_total": len(tasks), "tasks_required": len(required_tasks),
    "tasks_optional": len(tasks) - len(required_tasks),
}
require(manifest.get("counts") == computed, "Manifest count mismatch")
require(evidence.get("execution", {}).get("status") == "not_run", "Evidence template contains a false run")
if manifest.get("selection_status") == "candidate_not_selected":
    require(all(t.get("status") == "not_started" for t in tasks), "Unselected candidate has active/completed tasks")
    require(all(f.get("implementation_status") == "not_started" for f in features), "Unselected candidate claims implementation")

result = {
    "status": "pass" if not errors else "fail",
    "scope": "proposal_structure_only_not_runtime_validation",
    "plan_id": PLAN_ID, **computed,
    "required_features_with_implementation_tasks": sum(bool((set(f["work_items"])-{"TASK-001", "TASK-033", "TASK-034"}) & required_tasks) for f in features if f["release_required"]),
    "dependency_graph": "acyclic" if not any("cycle" in e for e in errors) else "invalid",
    "markdown_files": markdown_count, "relative_links_checked": link_count,
    "integrity_files_checked": len(entries), "source_inventory_entries": len(inventory),
    "target_files_preserved_in_manifest": len(target.get("preserved_files", [])),
    "errors": errors,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)

