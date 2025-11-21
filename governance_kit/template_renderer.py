from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path
from typing import Dict

from .utils import ensure_directory

PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def build_placeholder_map(args: argparse.Namespace) -> Dict[str, str]:
    now = _dt.datetime.now(_dt.timezone.utc)
    install_date = now.date().isoformat()
    return {
        "PROJECT_NAME": args.project_name,
        "PROJECT_CODE": args.project_code,
        "PROJECT_OWNER": args.project_owner,
        "PRIMARY_AI_SYSTEM": args.primary_ai,
        "PRIMARY_DOMAIN": args.primary_domain,
        "INSTALL_DATE": install_date,
        "GOVERNANCE_KIT_VERSION": "3.0.0",
        "DRIFT_SHIELD_ENABLED": "true" if args.enable_drift_shield else "false",
    }


def render_template(text: str, mapping: Dict[str, str]) -> str:
    unknown = set()

    def _rep(m):
        key = m.group(1)
        if key in mapping:
            return mapping[key]
        unknown.add(key)
        return m.group(0)

    rendered = PLACEHOLDER_PATTERN.sub(_rep, text)
    if unknown:
        for key in sorted(unknown):
            print(f"[governance-kit] Warning: no value for {{{{{key}}}}}", file=sys.stderr)
    return rendered


def render_templates_into(target_project: Path, mapping: Dict[str, str], force: bool = False) -> None:
    pkg_root = Path(__file__).resolve().parent
    tpl_dir = pkg_root / "templates"
    if not tpl_dir.is_dir():
        raise SystemExit(f"Templates directory not found: {tpl_dir}")
    gov_dir = target_project / ".governance"
    ensure_directory(gov_dir)
    for tpl_path in sorted(tpl_dir.glob("*.tpl")):
        dest_name = tpl_path.name[:-4]
        dest_path = gov_dir / dest_name
        if dest_path.exists() and not force:
            print(f"[governance-kit] Skipping existing file: {dest_path}")
            continue
        text = tpl_path.read_text(encoding="utf-8")
        rendered = render_template(text, mapping)
        dest_path.write_text(rendered, encoding="utf-8")
        print(f"[governance-kit] Wrote {dest_path}")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Render governance-kit-v3 templates into a project.")
    p.add_argument("--target", required=True, help="Target project directory.")
    p.add_argument("--project-name", required=True, help="Human-readable project name.")
    p.add_argument("--project-code", required=True, help="Short project code or slug.")
    p.add_argument("--project-owner", required=True, help="Project owner.")
    p.add_argument("--primary-ai", required=True, help="Primary AI system used during development.")
    p.add_argument("--primary-domain", required=True, help="Primary domain of the project.")
    p.add_argument("--enable-drift-shield", action="store_true", help="Enable drift shield extras.")
    p.add_argument("--force", action="store_true", help="Overwrite existing governance files.")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        raise SystemExit(f"Target directory does not exist: {target}")
    mapping = build_placeholder_map(args)
    render_templates_into(target, mapping, force=args.force)


if __name__ == "__main__":
    main()