#!/usr/bin/env python3
import os, sys, yaml, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
def load_kept(path):
    try:
        with open(path, "r") as f:
            y = yaml.safe_load(f) or {}
        return set(y.get("kept", []))
    except Exception:
        return set()
def main():
    allow = set()
    if "--allow-list" in sys.argv:
        allow |= load_kept(sys.argv[sys.argv.index("--allow-list")+1])
    py_files = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.py")]
    imports = set()
    for pf in py_files:
        try:
            for line in open(ROOT/pf, "r", errors="ignore"):
                m = re.match(r'^\s*(?:from\s+([\w\.]+)|import\s+([\w\.]+))', line)
                if m:
                    imports.add((m.group(1) or m.group(2)).split('.')[0])
        except: pass
    orphans = []
    for pf in py_files:
        base = pathlib.Path(pf).stem
        if base not in imports and pf not in allow and not pf.startswith("scripts/"):
            orphans.append(pf)
    if orphans:
        print("Potential orphan .py files (allow via release.keep.yml):")
        for o in orphans: print(" -", o)
    sys.exit(0)
if __name__=="__main__":
    main()