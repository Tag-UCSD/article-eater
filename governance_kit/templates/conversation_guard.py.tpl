#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Dict, Tuple

DEFAULT_CONFIG_PATH = Path(".governance") / "GOVERNANCE_CONFIG.yml"


def load_json_with_comments(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {path}") from exc
    lines: List[str] = []
    for line in raw.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(line)
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


class CheckResult:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def summarize(self) -> str:
        if not self.errors and not self.warnings:
            return "No issues detected."
        lines: List[str] = []
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


def resolve_project_root() -> Path:
    this_file = Path(__file__).resolve()
    return this_file.parent.parent


def _load_config(project_root: Path, rel_path: Path) -> Dict[str, Any]:
    path = project_root / rel_path
    if not path.is_file():
        raise FileNotFoundError(f"Governance config not found: {path}")
    return load_json_with_comments(path)


def _check_system_vision(project_root: Path, cfg: Dict[str, Any], result: CheckResult) -> None:
    paths = cfg.get("paths", {})
    rel = paths.get("system_vision")
    if not rel:
        result.add_error("Config missing paths.system_vision.")
        return
    path = project_root / rel
    if not path.is_file():
        result.add_error(f"System vision file not found: {rel}")
        return
    text = safe_read_text(path)
    if count_nonempty_noncomment_lines(text) < 5:
        result.add_warning(f"System vision file {rel} exists but looks very short.")


def _check_project_constitution(project_root: Path, cfg: Dict[str, Any], result: CheckResult) -> None:
    paths = cfg.get("paths", {})
    rel = paths.get("project_constitution")
    if not rel:
        result.add_error("Config missing paths.project_constitution.")
        return
    path = project_root / rel
    if not path.is_file():
        result.add_error(f"Project constitution file not found: {rel}")
        return
    text = safe_read_text(path)
    if count_nonempty_noncomment_lines(text) < 5:
        result.add_warning(f"Project constitution file {rel} exists but looks very short.")


def _check_conversation_ledger(project_root: Path, cfg: Dict[str, Any], result: CheckResult) -> None:
    paths = cfg.get("paths", {})
    rel = paths.get("conversation_ledger")
    if not rel:
        result.add_error("Config missing paths.conversation_ledger.")
        return
    path = project_root / rel
    if not path.is_file():
        result.add_error(f"Conversation ledger file not found: {rel}")
        return
    try:
        ledger = load_json_with_comments(path)
    except Exception as exc:
        result.add_error(f"Failed to parse conversation ledger {rel}: {exc}")
        return
    entries = ledger.get("entries")
    if entries is None:
        result.add_error("Conversation ledger missing 'entries' list.")
        return
    if not isinstance(entries, list):
        result.add_error("Conversation ledger 'entries' must be a list.")
        return
    seen_ids = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            result.add_error(f"Ledger entry {idx} is not an object.")
            continue
        eid = entry.get("id")
        if not eid:
            result.add_error(f"Ledger entry {idx} missing 'id'.")
        elif eid in seen_ids:
            result.add_error(f"Ledger entry id '{eid}' is duplicated.")
        else:
            seen_ids.add(eid)
        for field in ("date", "ai_system", "topic", "decisions"):
            if field not in entry:
                result.add_error(f"Ledger entry {eid or idx} missing '{field}'.")
    if not entries:
        result.add_warning("Conversation ledger exists but contains no entries.")


def _check_drift_shield(project_root: Path, cfg: Dict[str, Any], result: CheckResult) -> None:
    drift = cfg.get("drift_shield", {})
    if not drift or not drift.get("enabled", False):
        return
    paths = cfg.get("paths", {})
    rel_keep = paths.get("release_keep")
    rel_dep = paths.get("deprecations")

    if not rel_keep:
        result.add_error("Drift shield enabled but paths.release_keep missing.")
    else:
        p = project_root / rel_keep
        if not p.is_file():
            result.add_error(f"release.keep file not found: {rel_keep}")
        else:
            try:
                data = load_json_with_comments(p)
                files = data.get("files", [])
                if not isinstance(files, list):
                    result.add_error("release.keep 'files' must be a list.")
                else:
                    for relpath in files:
                        candidate = project_root / relpath
                        if not candidate.exists():
                            result.add_warning(f"release.keep lists '{relpath}' but it does not exist.")
            except Exception as exc:
                result.add_error(f"Failed to parse release.keep: {exc}")

    if not rel_dep:
        result.add_error("Drift shield enabled but paths.deprecations missing.")
    else:
        p = project_root / rel_dep
        if not p.is_file():
            result.add_error(f"deprecations file not found: {rel_dep}")
        else:
            try:
                _ = load_json_with_comments(p)
            except Exception as exc:
                result.add_error(f"Failed to parse deprecations.yml: {exc}")


def run_checks(project_root: Path, config_rel: Path) -> Tuple[CheckResult, int]:
    result = CheckResult()
    try:
        cfg = _load_config(project_root, config_rel)
    except FileNotFoundError as exc:
        result.add_error(str(exc))
        return result, 1
    except Exception as exc:
        result.add_error(f"Failed to load governance config: {exc}")
        return result, 1

    _check_system_vision(project_root, cfg, result)
    _check_project_constitution(project_root, cfg, result)
    _check_conversation_ledger(project_root, cfg, result)
    _check_drift_shield(project_root, cfg, result)

    if result.errors:
        return result, 2
    return result, 0


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Run governance-kit-v3 checks.")
    p.add_argument("--config", default=str(DEFAULT_CONFIG_PATH),
                   help="Path to governance config relative to project root.")
    p.add_argument("--check-all", action="store_true", help="Run all checks (default).")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    project_root = resolve_project_root()
    config_rel = Path(args.config)
    result, code = run_checks(project_root, config_rel)
    print(result.summarize())
    raise SystemExit(code)


if __name__ == "__main__":
    main()