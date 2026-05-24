#!/bin/bash
# Helper script to run the draw.io diagram validator

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/validate-drawio.py" "$@"
