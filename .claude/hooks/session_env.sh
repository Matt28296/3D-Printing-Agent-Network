#!/bin/bash
# SessionStart hook: put the project's virtualenv first on PATH for every Bash command
# Claude runs. On Windows (Git Bash) it converts the path and makes `python3` work,
# because Windows venvs only contain python.exe.
[ -n "$CLAUDE_ENV_FILE" ] && [ -n "$CLAUDE_PROJECT_DIR" ] || exit 0
PROJ="$CLAUDE_PROJECT_DIR"
if command -v cygpath >/dev/null 2>&1; then PROJ="$(cygpath -u "$PROJ")"; fi
if [ -d "$PROJ/.venv/bin" ]; then
  echo "export VIRTUAL_ENV=\"$PROJ/.venv\"" >> "$CLAUDE_ENV_FILE"
  echo "export PATH=\"$PROJ/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
elif [ -d "$PROJ/.venv/Scripts" ]; then
  echo "export VIRTUAL_ENV=\"$PROJ/.venv\"" >> "$CLAUDE_ENV_FILE"
  echo "export PATH=\"$PROJ/.venv/Scripts:\$PATH\"" >> "$CLAUDE_ENV_FILE"
  echo "python3() { \"$PROJ/.venv/Scripts/python.exe\" \"\$@\"; }" >> "$CLAUDE_ENV_FILE"
fi
exit 0
