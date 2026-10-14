#!/usr/bin/env python3
"""Reference lint for an agent-memory folder. No dependencies.

    python3 lint/memlint.py <memory-dir> [--today YYYY-MM-DD]
    python3 lint/memlint.py --diff <old.md> <new.md>

Exit 1 on any ERROR. STALE lines are warnings for the weekly consolidation.
"""
import re
import sys
from datetime import date, timedelta
from pathlib import Path

MAX_NOW = 10
MAX_LOG_CHARS = 300
OVERDUE_DAYS = 7
ENTITY_KEYS = {"name", "description", "updated"}
ENTITY_OPTIONAL = {"aliases"}
DECISION_KEYS = {"name", "description", "decided", "status"}
DECISION_OPTIONAL = {"aliases"}
DECISION_LINES = ["**Decided:**", "**Why:**", "**Alternatives:**", "**Revisit if:**"]
STATUSES = {"active", "reversed", "revisit"}

DATE = r"\d{4}-\d{2}(?:-\d{2})?"
LOG_RE = re.compile(rf"^- \[({DATE})\] (.+)$")
SUPERSEDED_RE = re.compile(rf" — superseded ({DATE}), see \S.*$")
TODO_RE = re.compile(r"^- \[ \] (\d{4}-\d{2}-\d{2}) ")
ASK_RE = re.compile(r"^- \[ask \d{4}-\d{2}-\d{2}\] .+ — .+ — .+$")
INSTRUCTION_RE = re.compile(
    r"ignore (all |any )?(previous|prior|above) instructions|disregard (the|your) rules"
    r"|system prompt|you are now|from now on,? (you|always)|<\/?(system|instructions?)>",
    re.I,
)


def as_date(s):
    return date.fromisoformat(s if len(s) == 10 else s + "-01")


def split_doc(text):
    """Return (frontmatter dict or None, {section: [lines]}, body lines)."""
    fm, body = None, text.splitlines()
    if body and body[0] == "---" and "---" in body[1:]:
        end = body.index("---", 1)
        fm = {}
        for line in body[1:end]:
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.split(" #")[0].strip()
        body = body[end + 1:]
    sections, current = {}, None
    for line in body:
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current and line.startswith("- "):
            sections[current].append(line)
    return fm, sections, body


def words(s):
    return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 3}


def lint_entity(path, text, today, out):
    fm, sec, _ = split_doc(text)
    err = lambda m: out.append(("ERROR", path, m))
    if fm is None:
        return err("missing frontmatter")
    if missing := ENTITY_KEYS - fm.keys():
        err(f"missing keys: {sorted(missing)}")
    if extra := fm.keys() - ENTITY_KEYS - ENTITY_OPTIONAL:
        err(f"unknown keys: {sorted(extra)}")
    if fm.get("name") != path.stem:
        err("name must equal the filename")
    if not 20 <= len(fm.get("description", "")) <= 150:
        err("description must be 20-150 chars")
    now, log = sec.get("Now", []), sec.get("Log", [])
    if len(now) > MAX_NOW:
        err(f"Now has {len(now)} bullets (max {MAX_NOW})")
    newest, retired = None, []
    for line in log:
        m = LOG_RE.match(line)
        if not m:
            err(f"bad Log line: {line[:60]}")
            continue
        d, fact = as_date(m.group(1)), SUPERSEDED_RE.sub("", m.group(2))
        newest = max(newest or d, d)
        if d > today:
            err(f"future date in Log: {m.group(1)}")
        if len(fact) > MAX_LOG_CHARS:
            err(f"Log line over {MAX_LOG_CHARS} chars: [{m.group(1)}]")
        if " · " not in fact or not fact.rsplit(" · ", 1)[1].strip():
            err(f"Log line has no source: [{m.group(1)}]")
        if fact.startswith("belief:") and re.search(r"\d", re.sub(DATE, "", fact.rsplit(" · ", 1)[0])):
            err(f"digits in a belief line (numbers come from data): [{m.group(1)}]")
        if SUPERSEDED_RE.search(m.group(2)):
            retired.append((m.group(1), fact.rsplit(" · ", 1)[0]))
    try:
        if newest and as_date(fm.get("updated", "")) < newest:
            err(f"updated {fm['updated']} is older than newest Log line {newest}")
    except ValueError:
        err("updated is not a date")
    for bullet in now:
        if INSTRUCTION_RE.search(bullet):
            err(f"instruction-shaped text in Now: {bullet[:60]}")
        b = words(bullet)
        for d, old in retired:
            o = words(old)
            if o and len(b & o) / len(o) >= 0.6:
                out.append(("STALE", path, f"Now repeats a fact superseded in log {d}: {bullet[:70]}"))
    for line in log:
        if INSTRUCTION_RE.search(line):
            err(f"instruction-shaped text in Log: {line[:60]}")


def lint_decision(path, text, out):
    fm, _, body = split_doc(text)
    err = lambda m: out.append(("ERROR", path, m))
    if fm is None:
        return err("missing frontmatter")
    if missing := DECISION_KEYS - fm.keys():
        err(f"missing keys: {sorted(missing)}")
    if extra := fm.keys() - DECISION_KEYS - DECISION_OPTIONAL:
        err(f"unknown keys: {sorted(extra)}")
    if fm.get("status") not in STATUSES:
        err(f"status must be one of {sorted(STATUSES)}")
    lines = [l for l in body if l.strip()]
    if len(lines) != 4 or not all(l.startswith(p) for l, p in zip(lines, DECISION_LINES)):
        err("body must be exactly Decided / Why / Alternatives / Revisit if")


def lint_dir(root, today=None):
    root, today, out = Path(root), today or date.today(), []
    for sub in ("areas", "people"):
        for p in sorted((root / sub).glob("*.md")):
            lint_entity(p.relative_to(root), p.read_text(), today, out)
    for p in sorted((root / "decisions").glob("*.md")):
        lint_decision(p.relative_to(root), p.read_text(), out)
    if (root / "now.md").exists():
        for line in (root / "now.md").read_text().splitlines():
            m = TODO_RE.match(line)
            if m and as_date(m.group(1)) < today - timedelta(days=OVERDUE_DAYS):
                out.append(("STALE", Path("now.md"), f"overdue >{OVERDUE_DAYS}d: {line[6:76]}"))
    if (root / "inbox.md").exists():
        for line in (root / "inbox.md").read_text().splitlines():
            if line.startswith("- [ask") and not ASK_RE.match(line):
                out.append(("ERROR", Path("inbox.md"), f"bad ask line: {line[:60]}"))
    return out


def check_change(old_text, new_text):
    """A write that changes ## Now must add at least one Log line."""
    _, old, _ = split_doc(old_text)
    _, new, _ = split_doc(new_text)
    if old.get("Now", []) != new.get("Now", []) and not set(new.get("Log", [])) - set(old.get("Log", [])):
        return ["ERROR: Now changed without a new Log line"]
    return []


def main(argv):
    if argv[:1] == ["--diff"] and len(argv) == 3:
        problems = check_change(Path(argv[1]).read_text(), Path(argv[2]).read_text())
        print("\n".join(problems) or "ok")
        return 1 if problems else 0
    today = date.fromisoformat(argv[argv.index("--today") + 1]) if "--today" in argv else None
    out = lint_dir(argv[0], today)
    for level, path, msg in out:
        print(f"{level:5} {path}: {msg}")
    errors = sum(1 for o in out if o[0] == "ERROR")
    print(f"{errors} error(s), {len(out) - errors} stale flag(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
