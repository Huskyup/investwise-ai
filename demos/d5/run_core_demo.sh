#!/bin/sh
# Separate manual launcher; does not install packages or change app defaults.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
mode="${1:-replay}"
case "$mode" in live|replay) ;; *) echo "Usage: $0 [replay|live]" >&2; exit 2;; esac
d5_python="${INVESTWISE_D5_PYTHON:-$HOME/.venvs/investwise-d5/bin/python}"
if [ ! -x "$d5_python" ]; then
  echo "Create the Python 3.12 environment first; see demos/d5/core/README.md." >&2
  exit 2
fi
exec "$d5_python" -B demos/d5/core_demo.py --mode "$mode" --open
