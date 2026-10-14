# example: Millpond Bakery

A synthetic memory folder for a fictional neighborhood bakery. Everything here is made up.

What to look at:
- `areas/flour.md`: a supplier change. The old Log line is marked superseded, and the Now bullet was rewritten in the same write.
- `areas/menu.md`: a Now bullet that still states a superseded fact. The lint flags it STALE.
- `people/theo-varga.md`: a person file with fixed Now slots.
- `decisions/2026-03-04-switch-to-stone-milled-flour.md`: Decided / Why / Alternatives / Revisit if.
- `inbox.md`: an ambiguous fact ("she") parked for a human instead of guessed into a file.
- `now.md`: one action more than a week overdue, flagged STALE.

Run the lint from the repo root:

    python3 lint/memlint.py example --today 2026-04-20
