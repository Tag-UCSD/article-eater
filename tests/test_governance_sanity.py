import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
def test_governance_kit_present():
    must = [
        "Project_Constitution.md","release.keep.yml","deprecations.yml",
        ".github/workflows/governance.yml","CODEOWNERS",
        "scripts/check_governance.py","scripts/orphan_sweep.py",
        "scripts/public_surface_ledger.py","scripts/manifest_sha256.py",
        "reconstructor_min.py","deconcat.py","public_surface_ledger.json",
    ]
    missing = [m for m in must if not (ROOT / m).exists()]
    assert not missing, f"Missing governance files: {missing}"

def test_rules_contract_registered():
    ledger = json.loads((ROOT/'public_surface_ledger.json').read_text())
    assert any(c.get('file')=='contracts/rules_v1.md' for c in ledger.get('contracts', [])), 'rules contract missing from ledger'