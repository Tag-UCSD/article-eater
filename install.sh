#!/usr/bin/env bash
# governance-kit-v3 installer

set -e

find_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
  elif command -v python >/dev/null 2>&1; then
    echo "python"
  else
    echo ""
  fi
}

PYTHON_BIN="$(find_python)"

if [ -z "$PYTHON_BIN" ]; then
  echo "Error: Python 3.11+ is required but no python interpreter was found." >&2
  exit 1
fi

PY_VERSION_OK="$("$PYTHON_BIN" - << 'EOF'
import sys
print(int(sys.version_info >= (3, 11)))
EOF
)"

if [ "$PY_VERSION_OK" != "1" ]; then
  echo "Error: Python 3.11+ is required (detected lower version)." >&2
  exit 1
fi

TARGET_DIR="$1"

if [ -z "$TARGET_DIR" ]; then
  printf "Enter target project directory (absolute or relative): "
  read -r TARGET_DIR
fi

if [ -z "$TARGET_DIR" ]; then
  echo "Error: no target directory provided." >&2
  exit 1
fi

if [ -d "$TARGET_DIR" ]; then
  TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
else
  printf "Target directory does not exist. Create it? [y/N]: "
  read -r CREATE_ANSWER
  case "$CREATE_ANSWER" in
    y|Y|yes|YES)
      mkdir -p "$TARGET_DIR" || {
        echo "Error: could not create directory '$TARGET_DIR'." >&2
        exit 1
      }
      TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
      ;;
    *)
      echo "Aborting." >&2
      exit 1
      ;;
  esac
fi

printf "Project name: "
read -r PROJECT_NAME

printf "Project code (slug): "
read -r PROJECT_CODE

printf "Project owner: "
read -r PROJECT_OWNER

printf "Primary AI system (e.g. ChatGPT, Claude): "
read -r PRIMARY_AI_SYSTEM

printf "Primary domain: "
read -r PRIMARY_DOMAIN

printf "Enable drift shield extras? [Y/n]: "
read -r DRIFT_ANSWER
if [ -z "$DRIFT_ANSWER" ] || [ "$DRIFT_ANSWER" = "y" ] || [ "$DRIFT_ANSWER" = "Y" ] || [ "$DRIFT_ANSWER" = "yes" ] || [ "$DRIFT_ANSWER" = "YES" ]; then
  DRIFT_FLAG="--enable-drift-shield"
else
  DRIFT_FLAG=""
fi

"$PYTHON_BIN" -m governance_kit.template_renderer       --target "$TARGET_DIR"       --project-name "$PROJECT_NAME"       --project-code "$PROJECT_CODE"       --project-owner "$PROJECT_OWNER"       --primary-ai "$PRIMARY_AI_SYSTEM"       --primary-domain "$PRIMARY_DOMAIN"       $DRIFT_FLAG