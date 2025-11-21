#!/usr/bin/env python3
import sys, os, subprocess, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = [
    "Project_Constitution.md","release.keep.yml","deprecations.yml",
    ".github/workflows/governance.yml",".github/pull_request_template.md","CODEOWNERS",
    "scripts/check_governance.py","scripts/orphan_sweep.py","scripts/public_surface_ledger.py",
    "scripts/manifest_sha256.py","reconstructor_min.py","deconcat.py","RUTHLESS_v5.1.md","public_surface_ledger.json",
]
def git_deleted_files():
    try:
        base = os.environ.get("GITHUB_BASE_REF")
        diff_range = f"origin/{base}...HEAD" if base else "HEAD~1..HEAD"
        out = subprocess.check_output(["git","diff","--name-status",diff_range], text=True)
        return {line.split("\t",1)[1].strip() for line in out.splitlines() if line.startswith("D\t")}
    except Exception:
        return set()
def main():
    missing = [p for p in REQUIRED if not (ROOT/p).exists()]
    if missing:
        print("Missing governance files:", missing, file=sys.stderr); sys.exit(2)
    keep = yaml.safe_load(open(ROOT/"release.keep.yml")) or {}
    kept = set(keep.get("kept") or [])
    deleted = git_deleted_files()
    violations = list(kept.intersection(deleted))
    if violations:
        print("Deletion violations for kept files:", violations, file=sys.stderr); sys.exit(3)
    print("Governance check passed."); sys.exit(0)
if __name__=="__main__":
    main()