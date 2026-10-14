# Why

Things I tried first, and how they broke.

**Retrieval over raw transcripts.** Search finds the passage that matches the words in the question, not the one that is still true. A plan from March and its reversal in April both match; the model picks one. Answers got worse as history grew, which is the opposite of what memory is for.

**Rolling summaries.** A model rewrites "what we know" after each conversation. Each rewrite drops or bends a little, nobody can see what changed, and after a few weeks the summary states things no source ever said. There is no way to check a line, because it has no source.

**Letting the agent write its own rules.** Agents happily append "always do X" to their own memory. Some of those lines came from users, some from documents, and a few were prompt injections. Memory that can hold instructions is an attack surface.

**Numbers in memory.** A remembered figure is a snapshot. It goes stale silently and gets quoted with full confidence. Storing the query instead of the result fixed this.

What the rules in this repo do about it:
- Now/Log separates the answer from the evidence, so the current truth is small and every claim has a dated, sourced line behind it.
- Supersession instead of deletion keeps the history checkable and makes "what changed and when" a lookup.
- The lint makes the format a contract instead of a suggestion. A model can't drift it, because a bad write is rejected.
- The inbox gives ambiguity a place to go other than a guess.
- Fencing the generated context as data, and rejecting instruction-shaped lines, keeps memory from becoming a second system prompt.
