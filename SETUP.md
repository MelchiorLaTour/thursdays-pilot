# App setup

This repository exposes two local MCP servers:

- **DataBrain** searches the indexed document folder and returns cited paths.
- **Cynthia** checks whether a project has a Cynthia context manifest.

Both run on the user's computer over standard input/output. They do not need an API key
or a hosted server.

## 1. Build the local index

From the cloned repository:

```bash
cd ~/thursdays-pilot
bash bin/setup.sh
```

The last line must report more than zero documents indexed. To use another local folder:

```bash
bash bin/setup.sh ~/Documents/Clients
```

The setup creates `.engine/` beside the repository. It does not copy, move, rename, or
upload the source documents.

## 2. Claude Desktop

The simplest route is to double-click `bundles/databrain.mcpb` and choose the folder that
contains the `.engine/` directory. Install `bundles/cynthia.mcpb` the same way if Cynthia
project-status checks are wanted in the conversation app.

If the app asks for a folder, choose `~/thursdays-pilot` (or the folder passed to
`bin/setup.sh`), then quit and reopen Claude Desktop. Start a new conversation and ask:

> Search the documents for the rate discount floor.

Claude should expose `databrain_search`, `databrain_read`, and
`databrain_abstain_check` as tools.

## 3. Codex

Register the same DataBrain server with the Codex CLI:

```bash
codex mcp add databrain-pilot -- \
  ~/thursdays-pilot/bundles/databrain/server/run.sh \
  ~/thursdays-pilot
```

Then start a fresh Codex session and ask it to search the example archive. The server
must list the same three `databrain_*` tools and return the indexed file paths.

To register Cynthia too:

```bash
codex mcp add cynthia-pilot -- \
  ~/thursdays-pilot/bundles/cynthia/server/run.sh
```

Cynthia uses `CYNTHIA_HOME` if the local Cynthia implementation is not at its default
path. The project-status tool is a visibility check; it does not route task content or
read the project's files.

## 4. What to show in the meeting

Use the synthetic example archive first. Show one question that finds a source, then one
question that is absent and produces an abstention signal. Only connect the client's own
documents after they explicitly choose the folder and approve the scope.

The setup is free for the client and remains under their control: their files, index, and
local MCP process stay on their machine. The text of any passage the model reads still
becomes part of that model provider's conversation, as with any other chat.
