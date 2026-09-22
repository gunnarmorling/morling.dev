#!/usr/bin/env bash
# Build a self-contained copy of the deck, for handing to someone else or serving from a
# machine with no network. Only the files the deck references are copied: the working
# directory also holds inputs/, earlier deck versions, the cut slides and several hundred
# candidate images, none of which should travel.
#
#   _tools/export.sh [out-dir] [--no-notes] [--optimise] [--standalone]
#
# --optimise re-encodes the copied images and caps them at twice the slide width. It needs
# Pillow; set PYTHON to an interpreter that has it. The deck directory is never touched.
#
# --standalone writes the deck into index.html instead of beside it, so the export opens from the
# file system. Without it reveal fetches slides.md, which a browser refuses to do over file://.
#
# The chosen deck is copied to slides.md, which is what index.html loads by default, so the
# link people get needs no query string. Serve the result with any static server:
#
#   jwebserver -d <out-dir> -b 0.0.0.0 -p 8000
#
# jwebserver binds to loopback without -b, and it lists directories, which is the other
# reason to serve an export rather than the working directory.
set -euo pipefail

DECK=slides.md
out=${1:-/tmp/hardwood-talk}
notes=yes
optimise=no
standalone=no
for arg in "$@"; do
  case $arg in
    --no-notes) notes=no ;;
    --optimise|--optimize) optimise=yes ;;
    --standalone) standalone=yes ;;
  esac
done
case $out in --*) out=/tmp/hardwood-talk ;; esac
# The venv beside this script if it has been made (see requirements.txt), else whatever python3
# is on the path. PYTHON in the environment wins over both.
here=$(cd "$(dirname "$0")" && pwd)
deck=$(dirname "$here")
if [ -z "${PYTHON:-}" ] && [ -x "$here/.venv/bin/python" ]; then
  PYTHON="$here/.venv/bin/python"
fi
PYTHON=${PYTHON:-python3}

cd "$deck"
[ -f "$DECK" ] || { echo "no $DECK in $deck" >&2; exit 1; }

rm -rf "$out"
mkdir -p "$out"
cp index.html custom.css helix.js "$out/"
cp -R vendor "$out/"
cp "$DECK" "$out/slides.md"

# Cut the Backburner, and with it everything after the closing slide. Truncating the file is the
# point: reveal's own data-visibility="hidden" would hide those slides while still shipping them
# inside slides.md, which anyone holding the link can read. The speaker notes are in there too,
# reachable at /slides.md or by pressing "s", so --no-notes takes them out the same way.
"$PYTHON" - "$out/slides.md" "$notes" <<'DECK_PY'
import re, sys

path, notes = sys.argv[1], sys.argv[2]
slides = re.split(r'\n\n---\n\n', open(path).read())

cut = next((i for i, s in enumerate(slides) if re.search(r'<!-- \.slide:[^>]*\bbackburner\b', s)), None)
if cut is None:
    sys.exit('export.sh: no slide marked "backburner" found, so the end of the talk is unclear.\n'
             '  Mark the divider with <!-- .slide: class="section backburner" --> or edit export.sh.')
dropped, slides = len(slides) - cut, slides[:cut]

if notes == 'no':
    slides = [re.split(r'(?m)^Note:', s)[0].rstrip() + '\n' for s in slides]

open(path, 'w').write('\n\n---\n\n'.join(slides))
print(f'  {len(slides)} slides, {dropped} dropped after the close'
      + (', notes stripped' if notes == 'no' else ''))
DECK_PY

# Every images/… path the *exported* deck mentions, and nothing else. Reading the truncated copy
# rather than the original keeps the cut slides' screenshots out: a static server lists /images/,
# so anything copied there is on show whether a slide points at it or not.
grep -oh 'images/[A-Za-z0-9._/-]*' "$out/slides.md" index.html custom.css helix.js | sort -u |
  while read -r f; do
    [ -f "$f" ] || { echo "missing: $f" >&2; continue; }
    mkdir -p "$out/$(dirname "$f")"
    cp "$f" "$out/$f"
  done

if [ "$optimise" = yes ]; then
  "$PYTHON" - "$out/images" <<'IMG_PY'
import io, os, sys

try:
    from PIL import Image, ImageChops
except ImportError:
    sys.exit('export.sh: --optimise needs Pillow.\n'
             '  pip install Pillow, or run with PYTHON=/path/to/an/interpreter/that/has/it')

# The slide is 1280 px wide, so a full-bleed image is never shown wider than 2560 device pixels,
# even on a retina screen where the browser scales the deck up. Detail past that cannot reach a
# viewer, so cap there; below it, only re-encode.
CAP = 2560
# Most of these images are screenshots and flat renders: a 256-colour palette costs them almost
# nothing and saves most of their bytes. Photographs band instead, so the palette is kept only
# when the mean error against the truecolour version stays under a fraction of one level, and
# only when it actually pays. MAE rather than the worst pixel, which a single stray edge decides.
MAX_MAE, MIN_GAIN = 2.0, 0.75


def encoded(img, fmt):
    buf = io.BytesIO()
    if fmt == 'PNG':
        img.save(buf, 'PNG', optimize=True)
    else:
        img.save(buf, 'JPEG', quality=82, optimize=True, progressive=True)
    return buf.getvalue()


def mean_error(a, b):
    histogram = ImageChops.difference(a.convert('RGB'), b.convert('RGB')).convert('L').histogram()
    return sum(i * n for i, n in enumerate(histogram)) / sum(histogram)


before = after = resized = quantised = kept = 0
for root, _, files in os.walk(sys.argv[1]):
    for name in sorted(files):
        path = os.path.join(root, name)
        fmt = {'.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG'}.get(os.path.splitext(name)[1].lower())
        if not fmt:
            continue
        was = os.path.getsize(path)
        before += was
        with Image.open(path) as im:
            im.load()
            if im.mode not in ('RGB', 'RGBA'):
                im = im.convert('RGBA')
            # BOX averages, which suits a screenshot and keeps the colour count down; LANCZOS is
            # sharper on a photograph, where JPEG carries the cost of the extra colours anyway.
            if max(im.size) > CAP:
                im.thumbnail((CAP, CAP), Image.BOX if fmt == 'PNG' else Image.LANCZOS)
                shrank = True
            else:
                shrank = False

            best, palette = encoded(im, fmt), False
            if fmt == 'PNG':
                flat = im.quantize(colors=256, method=Image.FASTOCTREE)
                data = encoded(flat, 'PNG')
                if len(data) < len(best) * MIN_GAIN and mean_error(im, flat) <= MAX_MAE:
                    best, palette = data, True

        if len(best) < was:
            with open(path, 'wb') as f:
                f.write(best)
            resized += shrank
            quantised += palette
        else:
            kept += 1
        after += os.path.getsize(path)

print(f'  images {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB'
      f' ({resized} resized to {CAP} px, {quantised} palettised, {kept} left as they were)')
IMG_PY
fi

if [ "$standalone" = yes ]; then
  "$PYTHON" - "$out" <<'ALONE_PY'
import os, re, sys

out = sys.argv[1]
html = open(os.path.join(out, 'index.html')).read()
deck = open(os.path.join(out, 'slides.md')).read()

# reveal reads an inline deck from a textarea, which the markdown may not close. It never does:
# the deck's own HTML is spans, divs and svg.
if '</textarea>' in deck:
    sys.exit('export.sh: the deck contains </textarea>, which cannot be inlined.')

section = re.search(r'<section\s+data-markdown=.*?</section>', html, re.S)
if not section:
    sys.exit('export.sh: no <section data-markdown=…> in index.html to replace.')
html = html.replace(section.group(0), (
    '<section data-markdown\n'
    '          data-separator="^\\r?\\n---\\r?\\n$"\n'
    '          data-separator-vertical="^\\r?\\n--\\r?\\n$"\n'
    '          data-separator-notes="^Note:"\n'
    '          data-charset="utf-8"\n'
    '        ><textarea data-template>\n' + deck + '\n</textarea></section>'))

# That block picks a deck file by query string and polls it for changes: both need a deck file.
picker = re.search(r'[ ]*// \?slides=.*?\n[ ]*\}\)\(\);\n', html, re.S)
if picker:
    html = html.replace(picker.group(0), '')

open(os.path.join(out, 'index.html'), 'w').write(html)
os.remove(os.path.join(out, 'slides.md'))
print(f'  deck inlined into index.html ({len(html) / 1024:.0f} kB), opens over file://')
ALONE_PY
fi

printf '%s: %s files, %s\n' "$out" "$(find "$out" -type f | wc -l | tr -d ' ')" "$(du -sh "$out" | cut -f1)"
# Anything the page pulls in at load time: a src, a stylesheet href, a CSS url(). Bare URLs in
# the slides are left alone, since the photo credits are written as plain text and the deck links
# them itself; they are text on a slide, not a request.
remote=$(grep -rhoE '(src|href)="https?://[^"]*|url\( *"?https?:[^)]*' "$out" \
  --include='*.html' --include='*.css' 2>/dev/null | sort -u || true)
[ -z "$remote" ] || { echo "still loads from the network:" >&2; echo "$remote" >&2; exit 1; }
