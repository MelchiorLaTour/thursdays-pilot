# Walkthrough — day one

Four things to run. Roughly fifteen minutes. Every command below was run on 20 September 2026
and produced the output shown.

Measured on that machine, that session: **14 files indexed in 1.3 seconds**, a query answered
in **60 milliseconds**, index size **64K**, **zero network calls** after the one-time clone.

---

## 0. Build the index

```
bash bin/setup.sh
```

That indexes the bundled example archive — a fabricated freelance advisory practice, 14 files:
6 PDFs, 4 Word documents, 4 notes. Proposals, a statement of work, a change order, two case
studies, a master services agreement, a rate card, a bio, meeting notes, a collections log.

To point it at your own folder instead:

```
bash bin/setup.sh ~/Documents/Clients
```

Watch what it prints: `extract: processed=10 extracted=10 failed=0`. It read ten PDFs and Word
files and pulled the text out of them. **Nothing was copied, moved, renamed or uploaded.** The
originals sit exactly where they were. Delete `.engine/` and you lose the index and nothing
else.

If you want to prove the point about where your data goes: turn off your wifi before running
any of the searches below. They all still work.

---

## 1. Ask it something you should know but can't remember

```
bash .engine/bin/fts.sh "rate discount floor hourly" 5
bash .engine/bin/look.sh "discount below"
```

The rate card comes back first, and `look.sh` shows the actual line:

> No discount below USD 350 per hour under any circumstance. A multi-month retainer already
> carries the discount; do not discount the retainer further. Where a client requests a
> reduction, remove scope rather than lowering the rate.

It did not summarise that, and it did not paraphrase it. It showed the sentence and the file it
came from, so you can open the file and check. That difference is what makes it usable in a
live client conversation instead of something you have to verify first.

---

## 2. Ask it the question that costs you money

```
bash .engine/bin/fts.sh "scope change order out of scope" 4
```

Four documents come back, in this order:

```
1   -3.92  12-notes-steering-halvorsen.md
2   -3.42  09-sow-retained-advisory.docx
3   -2.08  10-sow-amendment-a1.docx
4   -1.93  06-msa-template.pdf
```

Then read the top one:

```
bash .engine/bin/look.sh "out of scope"
```

> Chief of staff asked for a draft transaction announcement "as a favour, quickly". This is
> out of scope under SOW-2026-031-A. Said so. He pushed. Drafted it anyway. That is the third
> out-of-scope request this month and the second one I did before raising a change order. I am
> eroding my own contract.

And fourth on that list is the master agreement, clause 12:

> Work performed without a signed change order is performed at the Adviser's risk and is not
> billable.

**A meeting note, a statement of work, a change order and a master agreement, written months
apart, and it put the moment next to the rule that governs it.** Nobody tagged these files.
Nobody filed them into a system. They were sitting in a folder.

This is the one worth sitting with. Unbilled scope is the thing independent consultants lose
the most money to and track the least, because tracking it means re-reading your own archive,
which nobody does.

---

## 3. Ask it something that isn't there

```
bash .engine/bin/abstain-check.sh "CSRD sustainability assurance" "ESG reporting standard" "climate disclosure audit"
```

It runs your question three different ways and compares. Here, variant one finds nothing and
variants two and three both come back flagged weak, so:

```
DIVERGENT + WEAK → no strong shared hit; every variant weak-flagged.
   → READ the single best hit to confirm. If it does not actually answer, abstain honestly.
```

There is nothing about sustainability reporting in this archive, and it says so instead of
assembling a plausible-looking answer out of the nearest documents. A tool that invents a
precedent you then put in front of a client is worse than no tool at all.

Now the same check on something that *is* there:

```
bash .engine/bin/abstain-check.sh "rate discount floor" "hourly rate policy" "pricing discount rule"
```

```
CONVERGENT → 2+/3 variants share a strong top hit:
   08-rate-card-2026.docx
   → READ IT FIRST
```

Same mechanism, opposite answer. It is not refusing to be useful, it is refusing to guess.

---

## One rough edge, on purpose

`fts.sh` prints `⚠ WEAK MATCH` on some results that are correct. It fires whenever the top hit
matches fewer than half your query words, which happens easily on a four-word query against a
short document. It fires on the rate-card query in step 1 even though the answer is right
there.

The flag is deliberately pessimistic. That is exactly why `abstain-check.sh` exists: it runs
the question several ways and looks for **agreement between variants** rather than trusting a
single score. Treat a lone weak flag as "go read it", not as "it isn't there".

---

## What this does not do yet

Said plainly so nothing here is a surprise later.

- **No connection to SharePoint, OneDrive, Google Drive or email.** It reads a folder on your
  machine. If your material lives in a cloud workspace, it has to be synced to a local folder
  first.
- **No permissions.** Everything in the index is reachable by every query. That is fine for one
  person and it is not fine for a firm with client-confidentiality walls. A permission model is
  a build, not a setting.
- **It does not write your proposal.** It finds and shows you the material. Drafting from that
  material is a separate step and a separate decision.
- **Text only.** Charts, diagrams and the content of images are not searchable. A slide's
  words are; the picture on it is not.
- **Scanned PDFs need OCR first.** If a PDF is a photograph of a page rather than real text,
  `extract.sh` gets nothing from it and will report it as extracted with no content.
