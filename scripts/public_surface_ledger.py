#!/usr/bin/env python3
import sys, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "public_surface_ledger.json"
REQ = ["endpoints","cli","contracts"]
def write_ledger():
    ledger = {
        "endpoints":[
            {"method":"GET","path":"/api/rules"},
            {"method":"GET","path":"/api/rules/{rule_id}"},
            {"method":"POST","path":"/api/rules"},
            {"method":"GET","path":"/api/papers/{paper_id}"},
        ],
        "cli":[{"command":"aectl ingest --paper <path>"},{"command":"aectl build-ledger"}],
        "contracts":[{"module":"rules","version":"v1.0","file":"contracts/rules_v1.md"}]
    }
    LEDGER.write_text(json.dumps(ledger, indent=2))
def verify():
    if not LEDGER.exists(): print("public_surface_ledger.json missing", file=sys.stderr); sys.exit(2)
    data = json.loads(LEDGER.read_text())
    for s in REQ:
        if s not in data or not isinstance(data[s], list) or not data[s]:
            print(f"Ledger section '{s}' missing/empty", file=sys.stderr); sys.exit(3)
    print("Public surface ledger OK."); sys.exit(0)
if __name__=="__main__":
    if "--write" in sys.argv: write_ledger(); sys.exit(0)
    if "--verify" in sys.argv: verify()
    print("Usage: --write | --verify"); sys.exit(1)