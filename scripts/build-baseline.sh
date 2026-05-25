#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python -m py_compile gmail_organizer.py gmail_organizer_improved.py gmail_organizer_original.py
