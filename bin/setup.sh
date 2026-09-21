#!/usr/bin/env bash
# setup.sh — stand up the search layer over a folder of documents.
#
#   bin/setup.sh                      index the bundled example archive
#   bin/setup.sh ~/Documents/Clients  index YOUR folder instead
#
# What it does: clones the data-brain engine next to this repo, points it at the folder
# you named, extracts text from any PDFs and Word files, and builds a search index.
#
# What it does NOT do: copy, move, rename or upload a single one of your files. The engine
# is bash, ripgrep and sqlite. It makes no network calls after the one git clone below.
# Delete the whole thing and you lose nothing but the index.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$HERE/example-archive/files}"
ENGINE="$HERE/.engine"

die() { echo "setup: $1" >&2; exit 1; }

[ -d "$TARGET" ] || die "no such folder: $TARGET"
TARGET="$(cd "$TARGET" && pwd)"

# --- dependencies --------------------------------------------------------------------
missing=""
for b in git sqlite3 rg; do command -v "$b" >/dev/null 2>&1 || missing="$missing $b"; done
if [ -n "$missing" ]; then
  echo "setup: missing required tools:$missing" >&2
  echo "  on macOS:  brew install${missing}" >&2
  exit 1
fi
# pdftotext is only needed if there are PDFs to read.
if ! command -v pdftotext >/dev/null 2>&1; then
  if find "$TARGET" -iname '*.pdf' -print -quit | grep -q .; then
    die "that folder has PDFs but pdftotext is not installed (brew install poppler)."
  fi
  echo "note: pdftotext not installed — fine, no PDFs in that folder."
fi

# --- engine --------------------------------------------------------------------------
if [ -d "$ENGINE/.git" ]; then
  echo "engine already present at .engine — reusing it."
else
  echo "cloning the data-brain engine into .engine ..."
  git clone --quiet --depth 1 https://github.com/MelchiorLaTour/data-brain.git "$ENGINE" \
    || die "clone failed — is the repo reachable from this machine?"
fi

# --- point it at the folder ----------------------------------------------------------
# canon.sh is the single list of roots the engine reads. Rewrite CANON[] to just this one.
python3 - "$ENGINE/bin/canon.sh" "$TARGET" <<'PY'
import sys, io, re
path, target = sys.argv[1], sys.argv[2]
s = io.open(path, encoding="utf-8").read()
s = re.sub(r"CANON=\(\n.*?\n\)", 'CANON=(\n  "%s"\n)' % target, s, count=1, flags=re.S)
io.open(path, "w", encoding="utf-8").write(s)
PY
echo "indexing: $TARGET"

# --- build ---------------------------------------------------------------------------
cd "$ENGINE"
rm -rf moc
bash bin/build-index.sh  >/dev/null 2>&1 || die "build-index failed"
bash bin/ingest-root.sh "$TARGET" >/dev/null 2>&1 || die "ingest failed"
bash bin/extract.sh      2>&1 | grep -E '^extract:' || true
bash bin/build-fts.sh    2>&1 | grep -E '^built:'   || die "fts build failed"

rows=$(( $(wc -l < moc/index.tsv) - 1 ))
echo
echo "ready — $rows documents indexed, nothing copied or moved."
echo
echo "try:"
echo "  bash .engine/bin/fts.sh \"two or three keywords\" 5"
echo "  bash .engine/bin/look.sh \"a phrase from the top hit\""
echo "  bash .engine/bin/abstain-check.sh \"one phrasing\" \"another\" \"a third\""
echo
echo "WALKTHROUGH.md has a worked run against the example archive."
