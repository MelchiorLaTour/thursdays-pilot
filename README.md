# Thursday's Pilot

An asynchronous download of an entire AI setup, built for an independent consultant
who wants to use AI properly and get a head start on everyone else.

Not a demo and not a training deck. The working setup itself: how the tools are wired,
how the work actually gets done with them, and what to run on day one.

## Start here

| If you want | Open |
|---|---|
| To run it, in four steps | [`WALKTHROUGH.md`](WALKTHROUGH.md) |
| To point it at your own folder | `bash bin/setup.sh ~/your/folder` |
| To see what it is searching | [`example-archive/`](example-archive/) |

## What this is, concretely

A search layer over a folder of documents. It reads PDFs, Word files and notes where they
already sit, builds an index beside them, and answers questions by showing you the sentence
and the file it came from. When the answer is not in the folder, it says so rather than
assembling a plausible one.

The engine is bash, ripgrep and sqlite. No model, no API key, no account. After the one-time
clone in `bin/setup.sh` it makes **no network calls at all**, which is the honest version of
"your documents stay yours" — there is nowhere for them to go.

`WALKTHROUGH.md` closes with what it does not do yet. Read that part too.
