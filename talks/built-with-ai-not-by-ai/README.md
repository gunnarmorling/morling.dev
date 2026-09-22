# Built with AI, not by AI

Keynote deck for an internal developer conference.

| | |
|---|---|
| Slot | 75 minutes including Q&A; the talk runs about 60. |
| Audience | Senior/staff consultants and mid/junior developers. No management in the room. |
| Mandate | Change how they work, and open the day with energy. |
| Theme | Verify the output: the job moves from the *how* to the *what*. |
| Take-away | *Review the claim, not the diff.* |

`arc.md` is the working plan: the message, beats, slide numbers and minutes per section.

## Files

| Path | What it is |
|---|---|
| `slides.md` | **The deck**: a rise, a fall and a rise, told as a story. |
| `index.html` | reveal.js shell, loading everything from `vendor/`. Rarely touched. |
| `custom.css` | Layout overrides on the reveal `white` theme. |
| `helix.js` | The spiral reveal: a ring seen from above that a fragment tilts into a climbing helix. Use `<svg class="helix" data-helix data-turns="3">` plus a `data-helix-tilt` fragment. |
| `images/` | Only what `slides.md` shows. `images/sections/` holds the act dividers. |
| `vendor/` | reveal.js, its plugins and the two fonts, so the deck needs no network. See [vendor/README.md](vendor/README.md). |
| `_tools/` | `export.sh`, `serve.py`, `requirements.txt`, and the `prototypes/` and `timeline/` generators. |
| `_inputs/` | Working material: transcripts, sources, backdrop candidates, the images only the cuts file uses. Not in git, never travels with an export. |
| `slides-cuts.md` | Cut slides and the backburner beyond the cost chart, kept until the talk has been given. Some of its images are under `_inputs/`, so not in git. |
| `slides-prototypes.md` | Visual prototypes, written by `_tools/prototypes/make_prototypes.py`. Generated, so not in git. |

## Presenting

reveal.js fetches `slides.md`, so the deck needs a web server; opening `index.html` from the
file system shows a blank page. (`_tools/export.sh --standalone` builds a copy that doesn't.)

```bash
python3 _tools/serve.py        # → http://localhost:8000
```

On `localhost` the page reloads itself when the deck, `custom.css`, `helix.js` or `index.html`
changes, keeping the current slide and fragment; `serve.py` adds `Cache-Control: no-store` so a
reload never shows stale CSS. A changed image alone does not trigger it.

- `?slides=<file>.md` loads another deck from this directory, such as the cuts or the prototypes.
- `S` opens the speaker view with notes, timer and next-slide preview. A reload of the main
  window disconnects it; press `S` again.
- `Esc` is the slide overview, `?` lists every shortcut.
- `?grid` shows all slides as numbered thumbnails; `g` gets there from the current slide, and a
  click opens the deck at a thumbnail (Cmd/Ctrl-click for a new tab). Browser zoom sizes them.
- `?print-pdf` then print from Chrome — *Save as PDF*, *Landscape*, margins *None*, background
  graphics on. That PDF is what goes to Speaker Deck.

## Python

Everything here runs on the standard library except `export.sh --optimise`, which needs Pillow:

```bash
python3 -m venv _tools/.venv
_tools/.venv/bin/pip install -r _tools/requirements.txt
```

`export.sh` uses the `.venv` beside it when it exists, else `python3`; `PYTHON=…` overrides both.
Two paths point outside this directory, both in `make_prototypes.py`: Claude Code session
transcripts under `/claude-config`, and the Hardwood checkout it counts commits in, from
`HARDWOOD_REPO` (default `/workspace`).

## Sharing

```bash
_tools/export.sh /tmp/hardwood-talk --no-notes --optimise --standalone
jwebserver -d /tmp/hardwood-talk -b 0.0.0.0 -p 8000
```

The first argument is the output directory, **which `export.sh` deletes first**. It copies only
what the deck references, stops at the closing slide, and fails rather than ship anything that
still loads from the network. All three flags are optional:

| Flag | |
|---|---|
| `--no-notes` | Strips the speaker notes, which otherwise travel inside the markdown for anyone to read at `/slides.md` or with `S`. |
| `--optimise` | Re-encodes the images, 17 MB → 8.7 MB. Needs Pillow. |
| `--standalone` | Writes the deck into `index.html`, so the copy opens by double-clicking. A served copy does not need it. |

Export rather than serving this directory: a static server lists directories, and `_inputs/`,
the cut slides and the prototypes sit next to the deck. `jwebserver` also binds to loopback
unless given `-b`.

## Editing

One slide per `---`, with a blank line either side — the separator is anchored to `^\n---\n$`,
so a Markdown table or a setext underline cannot split a slide by accident:

```markdown
## A heading

Body text.

Note:
Speaker notes. Everything after `Note:` is notes, not slide content.

---

## Next slide
```

Every slide has one of four types, set with a comment on its first line:

| Type | Markup | Layout |
|---|---|---|
| Regular | *(none)* | Title pinned at the top, footer and slide number |
| Hero | `class="hero"` | One big sentence or quote, centred, no footer. `<span class="overline">` labels it |
| Hero image | `class="hero-image"` | One visual, centred; a `##` title becomes a quiet caption; no footer |
| Section | `class="section" data-state="section-slide" data-background-image="images/sections/….jpg" data-background-opacity="0.55"` | Act divider: dimmed full-bleed photo, big white caption, `<span class="credit">` for the photo credit, no footer |

Aim for a keynote mix: mostly hero and hero image, regular only where a list, table or code is
the point. Also: `class="statement"` for one sentence filling the slide, `class="wide"` for a
payload wider than the text column, `<!-- .element: class="fragment" -->` to reveal on click,
`<em>` for the one word that carries a sentence, `<span class="aside">` for a quiet grey line.
Fenced code blocks are highlighted; keep them under ~12 lines.

## Section photos

From Flickr via Openverse, licences allowing commercial use, no share-alike, no no-derivatives.
Credits are on the slides and in `images/sections/credits.json`.

| File | Photo | Author | Licence | Link |
|---|---|---|---|---|
| `title.jpg` | "Wood Grain" | mrpolyonymous | CC BY 2.0 | https://flic.kr/p/a6j2Z7 |
| `the-magic.jpg` | "TNT" | Alex Holyoake | CC BY 2.0 | https://flic.kr/p/AN2ZRn |
| `midnight.jpg` | "Solitude" | \*rboed\* | CC BY 2.0 | https://flic.kr/p/FJ1h26 |
| `hinge.jpg` | "Rusty hinge" | ConspiracyofHappiness | CC BY 2.0 | https://flic.kr/p/KqAcY |
| `new-way.jpg` | "Mechanics' Institute spiral staircase, from above" | chad_k | CC BY 2.0 | https://flic.kr/p/6AH9Zu |
| `price-joy.jpg` | "Meteorite" | Michael Elleray | CC BY 2.0 | https://flic.kr/p/aCqL2a |
| `chapter-build-loop.jpg` | "Aerial view of roundabout on OR 57 in Forest Grove" | OregonDOT | CC BY 2.0 | https://flic.kr/p/2j22sUS |
| `chapter-make-fast.jpg` | "Intersting 1960s desk stopwatch 5" | Elsie esq. | CC BY 2.0 | https://flic.kr/p/i9NnnB |
| `chapter-review.jpg` | "Magnifying glass 6/5" | John 'Pathfinder' Lester | CC BY 2.0 | https://flic.kr/p/bUgBy5 |
| `chapter-raise-floor.jpg` | "Bae Rice Terraces (Kiangan, Ifugao)" | ~MVI~ (warped) | CC BY 2.0 | https://flic.kr/p/4kA93z |
| `piano.jpg` | "Piano keys" | OnceCaptured | CC BY 2.0 | https://flic.kr/p/iiCcNU |
