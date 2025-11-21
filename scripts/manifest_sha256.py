#!/usr/bin/env python3
import os, hashlib, pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[1]
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(65536), b""): h.update(c)
    return h.hexdigest()
def main():
    files=[]; total=0
    for p in ROOT.rglob("*"):
        if p.is_file() and p.name!="MANIFEST.sha256":
            size=p.stat().st_size; total+=size
            files.append({"path":str(p.relative_to(ROOT)),"size":size,"sha256":sha256(p)})
    (ROOT/"MANIFEST.sha256").write_text(json.dumps({"total_bytes":total,"file_count":len(files),"files":files}, indent=2))
    print("Wrote MANIFEST.sha256")
if __name__=="__main__":
    main()