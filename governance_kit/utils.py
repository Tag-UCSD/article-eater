from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List


def load_json_with_comments(path: Path) -> Any:
    lines: List[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(raw)
    text = "\n".join(lines).strip()
    if not text:
        raise ValueError(f"File {path} is empty or contains only comments.")
    return json.loads(text)


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def count_nonempty_noncomment_lines(text: str) -> int:
    count = 0
    for raw in text.splitlines():
        s = raw.lstrip()
        if not s:
            continue
        if s.startswith("#") or s.startswith(">") or s.startswith("//"):
            continue
        count += 1
    return count


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)