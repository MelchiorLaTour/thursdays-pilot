#!/usr/bin/env bash
# One-command install. Clones the pilot, indexes a folder, registers the search
# tool with Claude Desktop, and tells you the single manual step left.
#
#   curl -fsSL https://raw.githubusercontent.com/MelchiorLaTour/thursdays-pilot/main/install.sh | bash
#   curl -fsSL .../install.sh | bash -s -- ~/Documents/Clients     # index your own folder
#
# Everything runs on this computer. Nothing is uploaded. The only network call is
# the git clone on the line below.
set -uo pipefail

REPO=https://github.com/MelchiorLaTour/thursdays-pilot.git
DEST="${DEST:-$HOME/thursdays-pilot}"     # home folder on purpose: macOS gates Desktop,
TARGET="${1:-}"                            # Documents and Downloads, and a gated folder
CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

say()  { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  ok   %s\n' "$1"; }
die()  { printf '\ninstall: %s\n' "$1" >&2; exit 1; }

case "$DEST" in
  "$HOME"/Desktop/*|"$HOME"/Documents/*|"$HOME"/Downloads/*)
    die "$DEST is inside a folder macOS gates. Claude cannot read it and searches will
         silently return nothing. Re-run with DEST=\$HOME/thursdays-pilot" ;;
esac

say "1. Checking tools"
missing=""
for b in git sqlite3 rg; do command -v "$b" >/dev/null 2>&1 || missing="$missing $b"; done
if [ -n "$missing" ]; then
  command -v brew >/dev/null 2>&1 || die "missing:$missing and Homebrew is not installed. See https://brew.sh"
  echo "  installing:$missing"
  brew install ${missing//sqlite3/sqlite} >/dev/null 2>&1 || die "brew install failed for:$missing"
fi
ok "git, sqlite3, ripgrep present"
command -v pdftotext >/dev/null 2>&1 || echo "  note: pdftotext missing, PDFs will be skipped (brew install poppler)"

say "2. Getting the files"
if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull --quiet --ff-only 2>/dev/null && ok "updated $DEST" || ok "kept existing $DEST"
else
  git clone --quiet "$REPO" "$DEST" || die "clone failed"
  ok "cloned to $DEST"
fi

say "3. Building the index"
cd "$DEST" || die "cannot enter $DEST"
out="$(bash bin/setup.sh ${TARGET:+"$TARGET"} 2>&1)" || { echo "$out" | tail -5; die "setup failed"; }
rows="$(printf '%s' "$out" | sed -n 's/^ready[^0-9]*\([0-9][0-9]*\) documents.*/\1/p' | tail -1)"
[ -n "${rows:-}" ] && [ "$rows" -gt 0 ] 2>/dev/null \
  || die "indexed 0 documents. Nothing readable was found in ${TARGET:-the example archive}."
ok "$rows documents indexed"

say "4. Registering the tool with Claude Desktop"
[ -d "/Applications/Claude.app" ] || die "Claude Desktop is not installed"
PY=""; for p in /opt/homebrew/bin/python3 /usr/local/bin/python3 "$(command -v python3 2>/dev/null)"; do
  [ -n "${p:-}" ] && [ -x "$p" ] && "$p" -c 'import sys' >/dev/null 2>&1 && { PY="$p"; break; }
done
[ -n "$PY" ] || die "no working python3 (brew install python)"
mkdir -p "$(dirname "$CFG")"
[ -f "$CFG" ] && cp "$CFG" "$CFG.bak-$(date +%Y%m%d%H%M%S)" && ok "backed up your existing config"
DEST="$DEST" "$PY" - <<'PY' || die "could not update the Claude config"
import json, os
cfg = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
dest = os.environ["DEST"]
try:
    with open(cfg) as fh: d = json.load(fh)
except Exception:
    d = {}
d.setdefault("mcpServers", {})["databrain"] = {
    "command": f"{dest}/bundles/databrain/server/run.sh",
    "args": [dest],
}
with open(cfg, "w") as fh: json.dump(d, fh, indent=2)
print("  ok   databrain registered")
PY
chmod +x "$DEST"/bundles/*/server/run.sh 2>/dev/null

say "Done. One step left, and only you can do it."
echo "  Quit Claude Desktop and open it again. It loads tools at launch."
echo
echo "  Then ask it something about those documents."
echo "  Searching is local. File names come back from search; a passage is read only"
echo "  when Claude needs it, and that passage becomes part of the conversation."
