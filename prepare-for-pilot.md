# Prepare for pilot: what the client needs most, and what to offer

**Date:** 2026-09-23. **Pilot:** Thursday 2026-09-24, 12:00–13:00.
**Source reviewed:** `MelchiorLaTour/thursdays-pilot` (private), commit `8586463`, read on
2026-09-23. Files read: `README.md`, `WALKTHROUGH.md`, `SETUP.md`, `INSTALL.md`,
`CLAUDE-APP-MCP.md`, the fourteen `example-archive/source-text/` files, and both MCP servers
(`bundles/databrain/server/main.py`, `bundles/cynthia/server/main.py`).

## Evidence status, read this first

- The repo never names the client. It says only "an independent consultant".
  `BUSINESS-PLAN.md` and `research/field-test-and-milestones.md` record that the counterparty,
  sponsor, payment and data scope for 24 September are not yet recorded.
- The 14-file example archive is **fabricated** (`example-archive/README.md`). Every need below
  is inferred from what Melchior chose to build into it. **No need in this file has been
  confirmed by the client answering a question.**
- Treat the ranking as a set of hypotheses to test on Thursday, not as findings. This matches
  the status of every row in `consulting-client-needs-2026-09-22.md`.

## What the pilot actually is

- A local search layer over a folder of documents: bash, ripgrep and sqlite. No model, no API
  key, no account, and no network calls after the one-time clone in `bin/setup.sh`.
- Two MCP servers, shipped as `.mcpb` bundles for Claude Desktop and as `codex mcp add`
  commands for Codex.
  - **DataBrain**: `databrain_search` (paths and scores only), `databrain_read` (capped
    excerpt of one file), `databrain_abstain_check` (runs 2–3 phrasings, reports agreement).
  - **Cynthia**: `cynthia_project_status` (does a project have a context manifest). Unrelated
    to any client need below.
- Measured by the author on 2026-09-20: 14 files indexed in 1.3 s, a query in 60 ms, 64K index.
  Author-measured only, not independently reproduced.
- The repo's own list of what it does not do: no SharePoint, OneDrive, Google Drive or email
  connector; no permission model; does not write the proposal; text only; scanned PDFs need
  OCR first.

## The biggest need: money earned but not collected

The example archive is built around three leaks. Together they are the strongest signal in the
repo about what Melchior believes this client loses money on.

### 1. Unbilled scope creep (largest)

- `WALKTHROUGH.md` states it directly: unbilled scope is "the thing independent consultants
  lose the most money to and track the least".
- Halvorsen retainer: four out-of-scope requests between 14 July and 8 August. Three were done
  before a change order existed, so they were at the adviser's own risk (MSA clause 12).
  Change order A1 recovered USD 13,175 (31 hours at USD 425).
- Steering notes, 8 August: "I am eroding my own contract."
- Northwind: the engagement ran 62 hours over estimate and 41 hours were absorbed, because
  crisis hours were not separated from advisory hours in the proposal.

### 2. Late payment that is never enforced

- Four of four invoices were paid late; interest was charged on none.
- Average days-to-cash is 46 against 30-day terms, which the collections log values at
  roughly sixteen days of working capital lent to clients for free.
- MSA clause 15 (4 percent above base after 45 days) has never been invoked.

### 3. Pricing discipline

- Rate card RC-2026: no discount below USD 350/hour, and the retainer already carries its
  discount. Useful, but lower money impact than 1 and 2.

### The gap in the pilot itself

The pilot only answers questions when the client thinks to ask them. It is retrospective. It
can show the SOW and clause 12 after the free work is done. The need is a check that fires
before the work is done, and a prompt that fires when an invoice is overdue. Search alone does
not do either.

## Top 10 offers, ranked

Ranked by money impact first, then by how close we already are to delivering it.
**Now** means the current search layer is enough. **Build** means new work.

| # | Offer | What it does | Status |
|---|---|---|---|
| 1 | Scope-creep guard | Client request goes in; it checks the SOW out-of-scope list and MSA clause 12, cites both, and drafts the change order | Build (light) |
| 2 | Collections enforcer | Tracks each invoice against its terms, flags anything past the interest trigger, drafts the reminder | Build (needs invoice data) |
| 3 | Proposal and RFP assembly | Pulls past proposals, case studies and bio with citations; applies rules such as "prior-firm work by sector only, never by client name" | Now for retrieval, build for drafting |
| 4 | Pricing guardrail | Answers "can I discount?" with the cited rate-card sentence; prompts the separate crisis-hour rate | Now |
| 5 | Estimate-vs-actual reconciliation | Compares hours quoted with hours worked per SOW, so an overrun is caught mid-engagement | Build (needs his time data) |
| 6 | Meeting-notes commitment tracker | Pulls actions and "get this in writing" items from notes and resurfaces them before the next meeting | Build (light) |
| 7 | Contract clause comparison | Compares a client-redlined MSA to his standard positions (liability cap, IP); flags differences, gives no legal advice | Build |
| 8 | Post-engagement capture | Turns a finished engagement's lessons into archive entries that feed later proposals | Build (light) |
| 9 | Methodology reuse kit | Generates artifacts such as the stakeholder scoring sheet from his own method notes | Build |
| 10 | Real-archive enablers | OCR for scanned PDFs, OneDrive/SharePoint sync, a Windows path | Build |

Offer 10 is closer to a gate than an offer. `INSTALL.md` tells the user not to keep the folder
in OneDrive, Dropbox, Google Drive or iCloud, and that is probably where a real archive lives.
Until it is solved, the client only ever sees the synthetic demo.

## Constraints on what we say Thursday

- **No price.** D14, D16 and D20: unpaid discovery, Melchior attends alone, no price discussed.
- **Build items are not day-one scope.** D61: say "on the roadmap, not yet priced". Do not
  describe the D39 scope items as included.
- **Architecture-level builds go through the audit rule.** Offers 2 and 5 need his real invoice
  and time data, which means new data contracts and access. `AGENTS.md` requires a written
  plan and a Codex (Astra) audit before implementation. Codex quota is exhausted until 10/15
  (`dai-sustaining-agents-2026-09-23`), so the fallback plan auditor applies.
- **Do not claim more than the demo does.** `research/DAI-AUDIT-mistakes-to-fix-prior-pilot.md`
  §1 already says the claim should be spoken aloud in the room.

## Defect found in the pilot repo

`databrain_read` in `bundles/databrain/server/main.py` opens any path the model passes it. It
checks `os.path.isfile` and nothing else, so it is not confined to the indexed folder. This
undercuts the "search returns paths only" privacy story in `CLAUDE-APP-MCP.md`. Fix it before
the server is pointed at the client's real folder. Restrict reads to paths under the indexed
root, and resolve symlinks before the check.

## Questions to test on Thursday

Use the five-question list in `consulting-client-needs-2026-09-22.md` §3 as the base. To test
this file's ranking, add two:

1. "The last time you did work that wasn't in the contract, how did you find out afterwards,
   and what did it cost?" Tests offer 1.
2. "How long did your last invoice take to be paid, and what did you do about it?" Tests
   offer 2.

If the answer to either is "that doesn't happen to me", the ranking above is wrong and offer 3
moves to the top.

## Not done

- The linked "Setup audit" artifact on the pilot README was not opened; it is private to
  Gonzague.
- The pilot was not run. All numbers in "What the pilot actually is" are the author's, quoted.
- No client, price or timeline is asserted anywhere in this file.
