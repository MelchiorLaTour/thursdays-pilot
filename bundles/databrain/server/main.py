#!/usr/bin/env python3
"""Databrain MCP server: local search over Melchior's notes, over stdio.

Privacy design, on purpose. `databrain_search` returns paths and relevance scores
only, never note text. Note content leaves the disk only when the model explicitly
calls `databrain_read` on one path, and even then it is capped. That keeps the
default interaction from pouring the archive into a hosted conversation.

Engine is bash + ripgrep + sqlite. No network calls, no API keys, no model.
"""
import json
import os
import subprocess
import sys

# Where the search engine lives. Order: first CLI argument, then env, then the default.
# The argument is what the installed bundle passes, from the folder the user picks at install.
# A pilot folder (one that ran setup.sh) keeps its engine in `.engine`, so accept either shape.
def _resolve_brain(raw):
    base = os.path.abspath(os.path.expanduser(raw))
    if os.path.isdir(os.path.join(base, ".engine", "bin")):
        return os.path.join(base, ".engine")
    return base


BRAIN = _resolve_brain(
    sys.argv[1] if len(sys.argv) > 1
    else os.environ.get("DATABRAIN_HOME", "~/Claude/Databrain")
)
BIN = os.path.join(BRAIN, "bin")
PROTOCOL = "2025-06-18"
READ_CAP = int(os.environ.get("DATABRAIN_READ_CAP", "1200"))
TIMEOUT = 60

TOOLS = [
    {
        "name": "databrain_search",
        "description": (
            "Search Melchior's personal knowledge base (Databrain) by keyword. Use this for "
            "any question about his own notes, ideas, people, projects or life, BEFORE "
            "answering from memory or asking him. Returns ranked file paths and scores only, "
            "no note text. A 'WEAK MATCH' marker means the answer is probably not in the "
            "brain, and saying so is the correct answer. Pass content keywords, not a "
            "sentence. Call databrain_read on a path to see its text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Content keywords, not a full sentence."},
                "limit": {"type": "integer", "description": "Max hits, default 5.", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "databrain_read",
        "description": (
            "Read a capped excerpt of ONE note returned by databrain_search. This is the only "
            "tool that returns note text, so call it deliberately and only for paths you need."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "A path exactly as databrain_search printed it."},
                "chars": {"type": "integer", "description": f"Excerpt cap, default {READ_CAP}."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "databrain_abstain_check",
        "description": (
            "Run the same question as 2 or 3 differently worded queries and report whether they "
            "converge on the same note. Use before relying on a Databrain answer. CONVERGENT "
            "means several phrasings agree; MIXED or weak means answer 'not in the brain'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "variants": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Two or three phrasings of the same question.",
                }
            },
            "required": ["variants"],
        },
    },
]


# Hosts launch MCP servers with a minimal PATH, so Homebrew and MacPorts are invisible and
# the engine's dependencies vanish. fts.sh exits 0 and prints nothing when ripgrep is absent,
# which would surface as an empty search result rather than an error. Rebuild PATH here and
# check the dependencies up front, so a broken install says so instead of looking empty.
_EXTRA_PATH = ["/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin", "/usr/bin", "/bin"]
REQUIRED = ("rg", "sqlite3")


def _env():
    env = dict(os.environ)
    parts = _EXTRA_PATH + [p for p in env.get("PATH", "").split(os.pathsep) if p]
    seen, ordered = set(), []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            ordered.append(p)
    env["PATH"] = os.pathsep.join(ordered)
    return env


def _missing_deps(env):
    from shutil import which
    return [b for b in REQUIRED if not which(b, path=env["PATH"])]


def run(script, args):
    path = os.path.join(BIN, script)
    if not os.path.isfile(path):
        # A macOS privacy gate makes a folder look empty rather than refusing loudly, so name
        # that case explicitly instead of blaming the user's folder choice.
        gated = ("/Desktop/", "/Documents/", "/Downloads/")
        if any(g in BRAIN + "/" for g in gated):
            return ("Databrain cannot read " + BRAIN + ". That folder is inside Desktop, Documents "
                    "or Downloads, which macOS gates, and this app has not been granted access. "
                    "Either move the folder to your home folder, or turn this app on under "
                    "System Settings > Privacy & Security > Full Disk Access and restart it.")
        return f"Databrain engine not found at {path}. Point the server at the folder you ran setup.sh in."
    env = _env()
    missing = _missing_deps(env)
    if missing:
        return ("Databrain cannot run: missing " + ", ".join(missing) +
                ". Install with: brew install " + " ".join(
                    {"rg": "ripgrep", "sqlite3": "sqlite"}[m] for m in missing))
    try:
        r = subprocess.run(["bash", path, *args], capture_output=True, text=True,
                           timeout=TIMEOUT, env=env)
    except subprocess.TimeoutExpired:
        return f"{script} timed out after {TIMEOUT}s."
    out = (r.stdout or "").strip()
    if out:
        return out
    err = (r.stderr or "").strip()
    if err:
        return f"{script} failed (exit {r.returncode}): {err}"
    return (f"{script} returned nothing (exit {r.returncode}). The index is probably empty. "
            f"Re-run setup.sh and check it reports more than 0 documents indexed.")


def strip_bodies(text):
    """Keep ranked-hit lines and advisory lines; drop anything that looks like note text.

    A ranked line is '  1   -2.40  <path>'. Everything else is passed through only if it is
    an advisory (warning marker), so snippets can never ride along by accident.
    """
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        parts = s.split(None, 2)
        ranked = len(parts) == 3 and parts[0].rstrip(".").isdigit()
        if ranked or s.startswith(("⚠", "no matches", "no content words", "──", "CONVERGENT", "MIXED", "ABSTAIN")):
            kept.append(s)
    return "\n".join(kept) or text


def reply(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def call(name, args):
    if name == "databrain_search":
        return strip_bodies(run("fts.sh", [args.get("query", ""), str(args.get("limit", 5))]))
    if name == "databrain_abstain_check":
        variants = [v for v in args.get("variants", []) if v][:3]
        if not variants:
            return "Pass two or three phrasings."
        return strip_bodies(run("abstain-check.sh", variants))
    if name == "databrain_read":
        path = os.path.expanduser(args.get("path", ""))
        cap = int(args.get("chars", READ_CAP))
        if not os.path.isfile(path):
            return f"No such note: {path}"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                body = fh.read(cap + 1)
        except OSError as exc:
            return f"Could not read {path}: {exc}"
        if len(body) > cap:
            return body[:cap] + f"\n[excerpt capped at {cap} chars]"
        return body
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method, rid = msg.get("method"), msg.get("id")
        if method == "initialize":
            reply(rid, {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                        "serverInfo": {"name": "databrain", "version": "1.0.0"}})
        elif method == "tools/list":
            reply(rid, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {})
            text = call(params.get("name"), params.get("arguments", {}))
            if text is None:
                reply(rid, error={"code": -32602, "message": f"Unknown tool {params.get('name')}"})
            else:
                reply(rid, {"content": [{"type": "text", "text": text}]})
        elif rid is not None:
            reply(rid, error={"code": -32601, "message": f"Unknown method {method}"})


if __name__ == "__main__":
    main()
