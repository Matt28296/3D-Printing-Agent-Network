#!/bin/bash
# Runs a Python safety hook with whatever Python is available. PROTECTED FILE.
# FAIL-CLOSED: if no working Python is found, exit 2 so the tool call is blocked
# (a hook that can't start would otherwise let every action through).
HOOK="$1"
DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
if command -v cygpath >/dev/null 2>&1; then DIR="$(cygpath -u "$DIR")"; fi
SCRIPT="$DIR/.claude/hooks/$HOOK"
works() { "$@" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; }
for cand in "$DIR/.venv/Scripts/python.exe" "$DIR/.venv/bin/python3" python3 python; do
  if works "$cand"; then exec "$cand" "$SCRIPT"; fi
done
if works py -3; then exec py -3 "$SCRIPT"; fi
if command -v uv >/dev/null 2>&1; then exec uv run --no-project --quiet python "$SCRIPT"; fi
echo "BLOCKED by project safety hook: no working Python found to run the safety checks. Install uv (see SETUP_PROMPT.md), open a new terminal and restart Claude Code." >&2
exit 2
