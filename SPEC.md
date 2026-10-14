# Spec

## 1. Principle
Every input (meeting transcripts, chats, corrections, documents, data refreshes) is distilled once, when it arrives, into structured files. Answers read the distilled current truth. Raw sources are kept unchanged as evidence and searched only for exact quotes. The hundredth transcript should be worth as much as the first.

## 2. Layout
| Path | What | Rewritable? |
|---|---|---|
| `profile.md` | Who or what this memory is about. Prose, ≤300 words, stable for months. | Only at consolidation |
| `now.md` | What is live right now: priorities, one section per active project with `Status:`, dated actions `- [ ] YYYY-MM-DD …`, `Links:`, open loops. No durable facts. | Yes |
| `areas/<slug>.md` | One file per ongoing subject. | Now yes, Log append-only |
| `people/<slug>.md` | One file per person or account. | Now yes, Log append-only |
| `decisions/YYYY-MM-DD-<slug>.md` | One file per real decision. The why is the point. | Only `status:` |
| `meetings/YYYY-MM-DD-<topic>.md` | Raw transcript with a `## Summary` header. | Never |
| `inbox.md` | Facts too ambiguous to file, waiting for a human. | Yes |
| `CONTEXT.md`, `INDEX.md` | Generated. What the agent reads; entity → files. | Never by hand |

Anything with a time, place or price in the next 30 days goes to `now.md` as a dated action, not into a Log.

## 3. File format
Areas and people:
```
---
name: <slug>                # equals the filename
description: <20–150 chars: what's here, when to read it>
aliases: [other names the text uses]   # optional
updated: YYYY-MM-DD         # bumped on every write; ≥ newest Log date
---
## Now
- <present-tense current truth, ≤10 bullets>
- Open: <unknowns to resolve>

## Log
- [YYYY-MM-DD] <one fact, ≤300 chars> · <source>
```
- People files use fixed Now slots: `Who / Role / Thread / Watch / Open`. `Watch` holds standing instructions about that person (how they like answers, what they care about).
- A Log line carries the event date, not the filing date. A plan or announcement is dated the day it was said. No future dates in a Log.
- A belief someone holds is written `belief: <who> thinks …` and contains no numbers. Numbers come from the data at answer time.
- Supersession: ` — superseded YYYY-MM-DD, see <pointer>` appended to the old line. Pointers are `see <path>`, `see <path> "<phrase>"` or `see log YYYY-MM-DD`. Never line numbers.

Decisions:
```
---
name: YYYY-MM-DD-<slug>
description: <one line>
decided: YYYY-MM-DD
status: active | reversed | revisit
---
**Decided:** …
**Why:** …
**Alternatives:** …
**Revisit if:** …
```

Inbox:
```
- [ask YYYY-MM-DD] <fact> — <target file> — <why unsure>
```

## 4. Pre-write check (run on every fact)
1. **Find targets.** Search the folder and `INDEX.md` for the key term. Every matching area, person and `now.md` entry is a target. A pronoun, "the X thing", or a term that matches two or more entities → defer to the inbox.
2. **Read** each target's Now and its relevant Log lines.
3. **Classify:**
   - SAME: already known. Skip.
   - NEW: append a Log line; edit Now if current truth changed.
   - CHANGE: append, mark the old line superseded, rewrite the Now bullet. If it supersedes two or more lines or ends a `now.md` project, update `now.md` too, and set `status: revisit` on any decision whose Why depends on it.
   - RESOLVES an Open item: append, remove the Open item.
   - TIME-BOUND: goes to `now.md`, not a Log.
   - DECISION: a choice someone made gets a `decisions/` file.
4. Bump `updated`.
5. Report one line: what was filed where.

**Durable test:** about a named entity that has a file, and still worth knowing in 30 days. Moods, one-offs and this-week logistics are not durable.

**File automatically:** stated facts, announced decisions, transcript facts. **Defer to the inbox:** inferences, rewrites of a person's Who/Role/Watch, sensitive personal topics, ambiguous referents.

## 5. Lint (on every write)
| Check | Result |
|---|---|
| Missing or unknown frontmatter key; `name` ≠ filename; description not 20–150 chars | reject |
| `updated` older than the newest Log date | reject (safe to auto-fix) |
| Now changed with no new Log line in the same write | reject |
| Log line without a source, over 300 chars, or with a future date | reject |
| Digits in a `belief:` line (dates excepted) | reject |
| More than 10 Now bullets | reject |
| Instruction-shaped text ("ignore previous instructions", "you are now", role tags) | reject |
| Decision body not exactly Decided / Why / Alternatives / Revisit if; bad `status` | reject |
| Malformed inbox `[ask]` line | reject |
| Now bullet that repeats a superseded Log line | STALE (warning) |
| `now.md` action more than 7 days overdue | STALE (warning) |

A rejected write is reverted and the fact goes to `inbox.md`. `lint/memlint.py` implements this table.

## 6. Context build
Before each turn, build `CONTEXT.md` in this order until the byte budget is spent: `now.md`, `profile.md`, the Now blocks relevant to the question, active decisions, the newest relevant Log lines, then STALE flags. Wrap it in a data fence and say it is data, not instructions. Measure the budget against answer latency.

Lookup order for the agent: context first; then search the folder; then read the whole file; raw meetings only for exact quotes.

## 7. Consolidation (weekly)
Deterministic first: lint every file, rebuild `INDEX.md`, list STALE flags, check each decision's "Revisit if" against new data. Then one model pass: rewrite each touched Now from its Log, fold superseded pairs into one line keeping both dates, and write the proposals to a review file. A proposal is applied only if it passes lint; otherwise a human confirms it. Never touch meetings or decision bodies. Flag any file that shrank more than 30%.

## 8. Robustness
- Version control commit per write; nightly backup.
- Idempotent distill: a re-pasted transcript classifies as SAME and is not duplicated.
- Every line traces back to a source.
- The database always beats memory for numbers.
- Sensitive personal content is not stored.

## 9. Tests worth having
- **Ceiling:** many meetings and chats over simulated weeks; late answers still use facts from the first meeting, and context stays in budget.
- **Supersede:** a belief changes mid-run; later answers use the new one and the old line is marked.
- **Inbox:** an ambiguous referent lands in the inbox, not in a file.
- **Poison:** instruction-shaped input never becomes a line.
