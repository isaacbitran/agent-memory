# agent-memory

How I give AI agents a memory that stays correct for months. I use it in a personal knowledge base and in an AI analyst a college football staff uses daily.

The idea: every fact is distilled once, on arrival, into small structured files. Agents answer from the distilled current truth, not from raw transcripts. A lint gate checks every write.

## The rules
1. One file per subject. Each file has `## Now` (current truth, at most 10 bullets) and `## Log` (append-only evidence, one dated fact per line with its source).
2. Now is the answer; Log is the proof. Changing a Now bullet requires a new Log line in the same write.
3. Nothing is deleted. A contradiction appends the new line and marks the old one `— superseded <date>, see <pointer>`. Newest date wins.
4. Every Log line names its source (meeting, chat, query, document). No source, no write.
5. Numbers never come from memory. Memory stores beliefs and decisions; numbers are recomputed from the database at answer time. The lint rejects digits in belief lines.
6. A lint gate runs on every write: frontmatter keys, `updated` at least the newest Log date, Now change without a Log line, more than 10 Now bullets, instruction-shaped text. Rejected writes go to `inbox.md` for a human.
7. Ambiguous facts (pronouns, a term matching two entities) are never guessed into a file. They wait in `inbox.md`.
8. A generated `CONTEXT.md` is rebuilt from the files within a byte budget and is what the agent reads at the start of every turn. It is fenced as data, never as instructions.
9. Weekly consolidation: a digest proposes Now rewrites, flags Now bullets contradicted by newer Log lines (STALE), and checks every decision's "revisit if".

## Layout
    profile.md  now.md  areas/<subject>.md  people/<slug>.md
    decisions/YYYY-MM-DD-<slug>.md  meetings/ (immutable)  inbox.md  CONTEXT.md (generated)

## What's here
- `SPEC.md`: the full rules, file format, pre-write procedure, lint table, consolidation.
- `WHY.md`: what broke before this.
- `lint/`: a reference lint in Python, no dependencies, with tests.
- `example/`: a synthetic memory for a fictional bakery, showing supersession, inbox deferral and STALE flags.

## Run
    python3 lint/memlint.py example --today 2026-04-20
    python3 lint/memlint.py --diff old.md new.md
    python3 -m unittest discover -s lint
