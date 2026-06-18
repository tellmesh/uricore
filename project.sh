#!/usr/bin/env bash
set -e
clear

# Prefer active venv, then .venv (uv), then legacy venv/
if [ -n "${VIRTUAL_ENV:-}" ] && [ -f "${VIRTUAL_ENV}/bin/pip" ]; then
  VENV="${VIRTUAL_ENV}"
elif [ -f ".venv/bin/pip" ]; then
  VENV=".venv"
elif [ -f "venv/bin/pip" ]; then
  VENV="venv"
else
  echo "Creating virtual environment (.venv)..."
  python3 -m venv .venv
  VENV=".venv"
fi

PIP="$VENV/bin/pip"
PY="$VENV/bin/python"

run_mod() {
  # Console scripts may have stale shebangs (e.g. after uricore → uricontrol rename).
  "$PY" -m "$@"
}

if [ ! -x "$PY" ]; then
  echo "Broken venv at $VENV — recreate with: rm -rf venv .venv && python3 -m venv .venv"
  exit 1
fi

#$PIP install -e .
#$PIP install regix --upgrade --quiet
#$PIP install pyqual --upgrade --quiet
$PIP install prefact --upgrade --quiet
$PIP install vallm --upgrade --quiet
$PIP install redup --upgrade --quiet
$PIP install glon --upgrade --quiet
$PIP install code2logic --upgrade --quiet
$PIP install code2llm --upgrade --quiet
#$VENV/bin/code2llm ./ -f toon,evolution,code2logic,project-yaml -o ./project --no-chunk
run_mod code2llm ./ -f all -o ./project --no-chunk --exclude '*.md'
#$VENV/bin/code2llm report --format all       # → all views

#$PIP install code2docs --upgrade --quiet
#$VENV/bin/code2docs ./ --readme-only
run_mod redup scan . --format toon --output ./project
#$VENV/bin/redup scan . --functions-only -f toon --output ./project
#$VENV/bin/vallm batch ./src --recursive --semantic --model qwen2.5-coder:7b
#$VENV/bin/vallm batch --parallel .
#$VENV/bin/vallm batch . --recursive --format toon --output ./project
run_mod prefact -a -e "examples/**"


$PIP install doql --upgrade --quiet
run_mod doql adopt . --format less --output app.doql.less --force

$PIP install sumd --upgrade --quiet
run_mod sumd .
run_mod sumr .


if [ -d "../goal/goal" ] && [ -f "../goal/pyproject.toml" ]; then
  "$PIP" install -e ../goal
  "$PIP" install -e ../goal --quiet
else
  "$PIP" install -U goal
  "$PIP" install goal --upgrade --quiet
fi
#$VENV/bin/goal -a

if [ -x "./tree.sh" ]; then
    bash ./tree.sh
elif command -v tree >/dev/null 2>&1; then
    tree -L 2
else
    echo "Skipping tree snapshot: ./tree.sh not found and 'tree' is not installed."
fi