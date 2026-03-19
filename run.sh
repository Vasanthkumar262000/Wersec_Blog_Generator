#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Use .venv if it has streamlit, otherwise venv
if [ -x "$ROOT/.venv/bin/streamlit" ]; then
    exec "$ROOT/.venv/bin/streamlit" run "$ROOT/app.py" "$@"
elif [ -x "$ROOT/venv/bin/streamlit" ]; then
    exec "$ROOT/venv/bin/streamlit" run "$ROOT/app.py" "$@"
else
    echo "Error: No Streamlit found. Install dependencies first:"
    echo "  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    echo "Then run: streamlit run app.py"
    exit 1
fi
