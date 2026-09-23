#!/bin/bash
# Find a Python that actually runs, then start the server.
# Two traps this avoids: desktop apps launch servers with a minimal PATH, and /usr/bin/python3
# on macOS can be a stub that refuses to run until Xcode's licence is accepted. So probe, don't assume.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
for P in /opt/homebrew/bin/python3 /usr/local/bin/python3 "$(command -v python3 2>/dev/null)" /usr/bin/python3; do
  [ -n "${P:-}" ] && [ -x "$P" ] || continue
  "$P" -c 'import sys' >/dev/null 2>&1 || continue
  exec "$P" "$DIR/main.py" "$@"
done
echo "databrain: no working python3 found on this machine. Install one with: brew install python" >&2
exit 1
