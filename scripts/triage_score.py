#!/usr/bin/env python3
"""Simple abstract triage scorer (recall-first).
Input JSON: [{"article_id": "...", "abstract": "..."}]
Output JSON: [{"article_id": "...", "score": 0.0..1.0, "keep": true/false, "rationale": "..."}]
"""
import sys, json, re
from difflib import SequenceMatcher

def score(a, q_terms):
    tokens = re.findall(r"[A-Za-z]{3,}", a.lower())
    overlap = len(set(tokens) & q_terms)/max(1, len(q_terms))
    sim = SequenceMatcher(None, " ".join(tokens)[:1200], " ".join(sorted(q_terms))[:1200]).ratio()
    return 0.7*overlap + 0.3*sim

def main():
    if len(sys.argv)<3:
        print("Usage: triage_score.py <input.json> <query_terms.txt>"); sys.exit(1)
    items = json.load(open(sys.argv[1]))
    q_terms = set(t.strip().lower() for t in open(sys.argv[2]).read().split() if t.strip())
    # Recall-first: low default threshold
    TH = 0.22
    out=[]
    for it in items:
        s = score(it.get("abstract",""), q_terms)
        keep = s >= TH or len(it.get("abstract",""))<60
        out.append({"article_id": it["article_id"], "score": round(s,4), "keep": bool(keep),
                    "rationale": "recall-first; threshold=0.22; borderline kept" if keep and s<0.3 else "similarity-based triage"})
    json.dump(out, sys.stdout, indent=2)
if __name__=="__main__": main()