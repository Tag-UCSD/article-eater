#!/usr/bin/env python3
import sys, pathlib
def deconcat(src, outdir):
    root=pathlib.Path(outdir); root.mkdir(parents=True, exist_ok=True)
    data=open(src,"r",encoding="utf-8",errors="replace").read()
    parts=data.split("