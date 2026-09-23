# Claude app: install via MCP

## Why this says MCP and not plugin

Claude Desktop has two separate extension systems and they use different settings pages.
**Plugins** are bundles of skills and commands, and they only load in Cowork and Code
sessions, never in ordinary chat. **MCP servers** are programs that give Claude tools, and
they work in ordinary chat. This is an MCP server, shipped as a `.mcpb` bundle, which is
simply an MCP server packaged for one-click install.

If someone goes looking under Plugins, they will not find it. It lives under Extensions.

## What an MCP server actually is

Not a remote machine, and nothing to sign up for. It is a program on your own computer that
offers Claude a set of tools. Claude Desktop starts it when the app launches, talks to it
through a pipe, and stops it when the app quits. No account, no URL, no hosting, no network.

In this case the program is a short Python script that searches an index of your documents.

## Install

1. Open the `bundles` folder in this repository.
2. Double-click **`databrain.mcpb`**.
3. Claude Desktop opens an install dialog and asks for **Your documents folder**. Choose the
   folder you ran `bin/setup.sh` in.
4. Click **Install**.

Done. Start a new conversation and ask something about those documents.

If double-clicking does nothing, open Claude Desktop and go to
`Settings > Extensions > Advanced settings > Extension Developer > Install Extension...`,
then choose the same file.

## The three tools it adds

| Tool | What it does |
|---|---|
| `databrain_search` | Ranked keyword search. Returns **file paths and scores only**, never document text. |
| `databrain_read` | Returns a capped excerpt of one file you name. This is the only tool that returns text. |
| `databrain_abstain_check` | Runs two or three phrasings of the same question and reports whether they agree. Disagreement means the answer probably is not in your documents. |

## What stays on your computer, and what does not

Searching is entirely local. The index is local. The program is local. It makes no network
calls, holds no API key, and sends nothing anywhere.

The honest limit: when Claude reads a passage to answer you, that passage becomes part of the
conversation, and conversations are stored by Anthropic like any other chat. Local search does
not make a hosted conversation private. What it does mean is that your whole archive is never
uploaded, and only the specific passage needed for an answer is ever read.

Search returning paths only is deliberate. A broad search physically cannot pour your
documents into a conversation, because the search tool has no way to return their contents.

## If it installs but finds nothing

Three causes, in the order they actually happen.

**The index is empty.** Re-run `bin/setup.sh` and read its last line. If it says
`0 documents indexed`, the folder is in a location the indexer skips. The usual culprit is a
path containing `Library`, which is where OneDrive, Dropbox, Google Drive and iCloud live on a
Mac. Move the documents to a plain folder under Documents and run it again.

**Ripgrep or SQLite is missing.** The server now says so explicitly rather than returning an
empty result. Fix with `brew install ripgrep sqlite`.

**You picked the wrong folder at install.** Remove the extension under
`Settings > Extensions` and install it again, choosing the folder that contains `.engine`.

## Removing it

`Settings > Extensions`, find Databrain, remove. Then delete this repository folder if you
want the index gone too. Your original documents were never inside it and are untouched.
