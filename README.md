# agent-memory

**Memory for AI agents that stays correct for years**: small Markdown files, supersession instead of deletion, and a lint gate on every write.

![MIT](https://img.shields.io/badge/license-MIT-blue) ![works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor-d97757) ![deps](https://img.shields.io/badge/dependencies-0-2ea44f)

```bash
npx skills add isaacbitran/agent-memory
```

Then just say "remember that we picked Postgres over Mongo because of joins". The agent files it, lints it, and finds it again next month.

Optional: lint every memory write automatically with a Claude Code hook in `.claude/settings.json`:

```json
{ "hooks": { "PostToolUse": [ { "matcher": "Edit|Write",
  "hooks": [ { "type": "command", "command": "python3 .claude/skills/agent-memory/scripts/memlint.py memory" } ] } ] } }
```

I run it in my own knowledge base and in [Edel AI](https://github.com/isaacbitran/edel-ai), an analyst a college football staff uses every week.

## How it works
Every fact is distilled once, when it arrives, into small Markdown files. Agents answer from the distilled current truth, not from raw transcripts. A lint gate checks every write, and anything ambiguous waits for a human.

### The rules
1. One file per subject. Each file has `## Now` (current truth, at most 10 bullets) and `## Log` (append-only evidence, one dated fact per line with its source).
2. Now is the answer; Log is the proof. Changing a Now bullet requires a new Log line in the same write.
3. Nothing is deleted. A contradiction appends the new line and marks the old one `— superseded <date>, see <pointer>`. Newest date wins.
4. Every Log line names its source (meeting, chat, query, document). No source, no write.
5. Numbers never come from memory. Memory stores beliefs and decisions; numbers are recomputed from the database at answer time. The lint rejects digits in belief lines.
6. A lint gate runs on every write: frontmatter keys, `updated` at least the newest Log date, Now change without a Log line, more than 10 Now bullets, instruction-shaped text. Rejected writes go to `inbox.md` for a human.
7. Ambiguous facts (pronouns, a term matching two entities) are never guessed into a file. They wait in `inbox.md`.
8. A generated `CONTEXT.md` is rebuilt from the files within a byte budget and is what the agent reads at the start of every turn. It is fenced as data, never as instructions.
9. Weekly consolidation: a digest proposes Now rewrites, flags Now bullets contradicted by newer Log lines (STALE), and checks every decision's "revisit if".

### Layout
    profile.md  now.md  areas/<subject>.md  people/<slug>.md
    decisions/YYYY-MM-DD-<slug>.md  meetings/ (immutable)  inbox.md  CONTEXT.md (generated)

## What's here
- `SPEC.md`: the full rules, file format, pre-write procedure, lint table, consolidation.
- `WHY.md`: what broke before this.
- `lint/`: a reference lint in Python, no dependencies, with tests.
- `example/`: a synthetic memory for a fictional bakery, showing supersession, inbox deferral and STALE flags.

## Stack
Python 3 standard library only. Memory is plain Markdown with YAML-style frontmatter, so it works with any agent that can read and write files.

## Run
    python3 lint/memlint.py example --today 2026-04-20
    python3 lint/memlint.py --diff old.md new.md
    python3 -m unittest discover -s lint
