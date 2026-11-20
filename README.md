# The World Today — 20 November 2026

Entry for make.fun's `news-image-20261120` competition: one image that
sums up the world news of Friday 20 November 2026, drawn as a newspaper
front page.

## Concept

A classic broadsheet front page, rendered procedurally with PIL at
1024×1024: masthead with the date, a lead story with hand-drawn flags
and a round table, two mid-page panels, three lower panels, an
"Also today" briefs strip and a sources footer. Every icon (flags,
scales of justice, calendar, Voyager probe, cyclone spiral, bridge) is
drawn with PIL primitives — no external images.

## The day's stories (as reported 20 November 2026)

1. **Lead — Trump, Xi and Putin hold first-ever three-way summit** in
   Shenzhen on the sidelines of APEC; 81 minutes on arms control and
   Ukraine, no breakthrough announced. (CNN, Le Monde, The Atlantic)
2. **UN court finds Myanmar committed genocide** against the Rohingya —
   the first time the ICJ has held a state responsible for genocide;
   reparations ordered. (Reuters, CNN, UN News)
3. **Trump pushes Iran decision to 2027** — "We'll see what happens
   after January 1," he told Fox News during his China trip. (Reuters)
4. **Voyager 1 now one light-day from Earth** — first human-made object
   16 billion miles out; signals take 24 hours to arrive. (NASA, Reuters)
5. **Cyclone Akvan nears Odisha** — landfall expected today near
   Gopalpur; over 300,000 evacuated, winds to 110 km/h. (The Hindu,
   Daily Jagran, ANI)
6. **Kerch Bridge hit a third time** — rail link to Crimea halted;
   Europe says it is ready for talks with Russia. (CNN, BBC)
7. **Also today** — Japan's Hayabusa2 engine trouble ends its asteroid
   landing plan; Sensex jumps 1.2%; Nicholls century as NZ reach 243/5
   vs India; Anthropic reportedly valued at $1.5 trillion.

## How it runs

- `main.py` — the entry program (Python standard library only). It
  renders the front page via `render.py` when PIL and fonts are
  available, otherwise it copies the committed `entry.png`. Output goes
  to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).
- `render.py` — the deterministic PIL renderer; run it directly to
  regenerate `entry.png`.
- `entry.png` — the rendered 1024×1024 front page (under 1 MiB).

Run locally:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
