#!/usr/bin/env python3
"""Cynthia MCP server: project-manifest discovery over stdio.

This is the portable half of Cynthia. Its discovery step used to exist only as a
Claude Code SessionStart hook, which is why it could not run in any other app.
As an MCP tool the same logic runs anywhere MCP does.

It reads only a project's own manifest file and reports whether one exists. It
never reads, sends or summarises task content.
"""
import json
import os
import sys
from pathlib import Path

CYNTHIA = os.environ.get("CYNTHIA_HOME",
                         os.path.expanduser("~/Claude/claude-action-plan/cynthia"))
TEMPLATE = os.path.join(CYNTHIA, "context-manifest.template.json")
PROTOCOL = "2025-06-18"
SYSTEM_SYMLINKS = {Path("/tmp"), Path("/var")}

TOOLS = [{
    "name": "cynthia_project_status",
    "description": (
        "Check whether Cynthia can see a project, by looking for its context-manifest.json. "
        "Call this before any routed or multi-model work in a project directory. Cynthia only "
        "knows a project exists when a manifest declares it, so a missing manifest means the "
        "project is invisible to it and one should be offered. Returns manifest state only, "
        "never project content."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {"type": "string",
                     "description": "Any path inside the project. The project root is found by walking up."}
        },
        "required": ["path"],
    },
}]


def _has_symlink_component(path):
    candidate = Path(path).absolute()
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current /= part
        if current.is_symlink():
            if current in SYSTEM_SYMLINKS:
                current = current.resolve()
            else:
                return True
    return False


def find_root(start):
    """Walk up to the nearest project marker, stopping before $HOME and /."""
    home, root = os.path.expanduser("~"), os.path.abspath(start)
    if os.path.isfile(root):
        root = os.path.dirname(root)
    while root not in ("/", home):
        for marker in (".git", "CLAUDE.md", "PROJECT.md"):
            if os.path.exists(os.path.join(root, marker)):
                return root
        root = os.path.dirname(root)
    return None


def status(path):
    if path is None or path == "":
        path = "."
    if not isinstance(path, str):
        return "Invalid project path."
    candidate = Path(path).expanduser()
    if _has_symlink_component(candidate):
        return "The requested path is not eligible for Cynthia discovery."
    if any(part.lower() == "sensitive" for part in candidate.parts):
        return "The requested path is not eligible for Cynthia discovery."
    try:
        resolved = candidate.resolve(strict=False)
    except OSError:
        return "No such path."
    if any(part.lower() == "sensitive" for part in resolved.parts):
        return "The requested path is not eligible for Cynthia discovery."
    path = os.fspath(resolved)
    if not os.path.exists(path):
        return "No such path."
    root = find_root(path)
    if not root:
        return ("The path is not inside a recognised project (no .git, CLAUDE.md or PROJECT.md "
                "found above it, stopping at the home directory). Cynthia does not apply here.")
    manifest = os.path.join(root, "context-manifest.json")
    if os.path.islink(manifest):
        return "The project manifest is not eligible for Cynthia discovery."
    if os.path.isfile(manifest):
        return "Cynthia: manifest found. Run the coordinator preflight before routed work."
    return ("Cynthia: no context manifest found, so Cynthia cannot see this project. "
            "Offer to create one from the configured template before routed work begins.")


def reply(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict):
            continue
        method, rid = msg.get("method"), msg.get("id")
        if method == "initialize":
            reply(rid, {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                        "serverInfo": {"name": "cynthia", "version": "1.0.0"}})
        elif method == "tools/list":
            reply(rid, {"tools": TOOLS})
        elif method == "tools/call":
            p = msg.get("params", {})
            if not isinstance(p, dict):
                reply(rid, error={"code": -32602, "message": "invalid_params"})
                continue
            if p.get("name") != "cynthia_project_status":
                reply(rid, error={"code": -32602, "message": "unknown_tool"})
                continue
            arguments = p.get("arguments", {})
            if not isinstance(arguments, dict):
                reply(rid, error={"code": -32602, "message": "invalid_params"})
                continue
            reply(rid, {"content": [{"type": "text", "text": status(arguments.get("path", "."))}]})
        elif rid is not None:
            reply(rid, error={"code": -32601, "message": "method_not_found"})


if __name__ == "__main__":
    main()
