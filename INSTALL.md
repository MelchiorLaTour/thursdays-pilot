# Installing a brain, every step

Written for someone who is not you. Every step happens on **their** computer. Nothing runs on
yours, nothing routes through yours, and you never see their documents. Their machine does the
indexing, their machine runs the search, their own Claude or ChatGPT account does the thinking.

Assumed: a Mac, and Claude Desktop already installed.

---

## Step 1. Get the files

Open `https://github.com/MelchiorLaTour/thursdays-pilot`

Click the green **Code** button, then **Download ZIP**.

Double-click the downloaded ZIP. It becomes a folder called `thursdays-pilot-main`.

Drag that folder to **Documents** and rename it `thursdays-pilot`.

> **Do not put it in a cloud folder.** Not OneDrive, not Dropbox, not Google Drive, not
> iCloud Drive. See the warning in Step 3, it matters more than it sounds.

*(Anyone comfortable with a terminal can skip all that with
`git clone https://github.com/MelchiorLaTour/thursdays-pilot.git`.)*

## Step 2. Check the two tools it needs

Open **Terminal** (Spotlight, type "Terminal", Enter). Paste this and press Enter:

    which git sqlite3 rg pdftotext

Four paths should print. If `rg` or `pdftotext` is missing:

    brew install ripgrep poppler

If `brew` itself is missing, install Homebrew from `https://brew.sh` first.

## Step 3. Build the index

Still in Terminal:

    cd ~/Documents/thursdays-pilot
    bin/setup.sh

That indexes the bundled example documents, so it proves the machine works before any real
files are involved. It takes a couple of seconds.

To index their real documents instead, pass the folder:

    bin/setup.sh ~/Documents/Clients

**Read the last line before continuing.** It says something like
`ready, 14 documents indexed`. If it says **`0 documents indexed`**, stop. The folder is in a
location the indexer skips, and the most common cause is a path containing `Library`, which is
where OneDrive, Dropbox, Google Drive and iCloud all live on a Mac. Move or copy the documents
to a plain folder under Documents and run it again.

Nothing was copied, moved or renamed. The originals are untouched. What was created is a search
index inside the `thursdays-pilot` folder.

## Step 4. Install the brain into Claude

In Finder, open `thursdays-pilot`, then the `bundles` folder.

Double-click **`databrain.mcpb`**.

Claude Desktop opens an install dialog. It asks for **Your documents folder**. Choose the
`thursdays-pilot` folder from Step 1. Click **Install**.

That is the whole installation. No config file, no API key, no account.

If double-clicking does nothing, open Claude Desktop and go to
`Settings > Extensions > Advanced settings > Extension Developer > Install Extension...`, then
pick the same file.

## Step 5. Use it

Open a new conversation in Claude and ask something that lives in those documents:

> What did we say about stakeholder mapping?

Claude searches the index, gets back a list of matching files, and reads the one it needs. If
nothing matches well, it says so rather than inventing an answer. That honest "I don't have
this" is the point of the thing.

---

## Where everything actually lives

| Thing | Where it runs | Who can see it |
|---|---|---|
| The documents | Their Mac, where they already were | Only them |
| The search index | Inside their `thursdays-pilot` folder | Only them |
| The search program | Their Mac, launched by Claude Desktop | Only them |
| The conversation | Their Claude account | Them and Anthropic |

Your computer appears nowhere in that table. You host nothing, you run nothing for them, and
you cannot read their files.

**The one honest caveat.** Searching is fully local, and search results are file names only.
But when Claude reads a note to answer, that text becomes part of the conversation, and
conversations live on the provider's servers, the same as anything else typed into Claude.
Local search does not make a hosted chat private. What it does mean is that their whole archive
is never uploaded, and only the specific passage needed for an answer is ever read.

## Uninstalling

Claude Desktop: `Settings > Extensions`, find Databrain, remove it.
Everything else: drag the `thursdays-pilot` folder to the Trash. The index dies with it, and
the original documents are untouched because they were never inside it.

---

## For ChatGPT instead of Claude

Harder, and it is OpenAI's design, not ours. ChatGPT cannot launch a program on a Mac. It only
calls web addresses. Reaching a local brain needs OpenAI's relay running on their machine, plus
an OpenAI Platform account with two API keys, billed separately from ChatGPT Plus.

If they use Codex, the command-line tool, it is one line and needs no keys at all:

    codex mcp add databrain -- python3 ~/Documents/thursdays-pilot/bundles/databrain/server/main.py ~/Documents/thursdays-pilot

Full detail is in `SETUP.md`.
