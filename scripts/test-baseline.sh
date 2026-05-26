#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python -m unittest -q test_copilot_instructions test_revvel_standards
