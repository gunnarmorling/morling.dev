# Vendored assets

The deck loads nothing from the network, so it runs on a conference wifi that has died, on a
laptop in flight mode, and from an export handed to someone else. Everything `index.html` needs
lives here.

| Path | What | Source |
|---|---|---|
| `reveal/*.css`, `reveal/reveal.min.js` | reveal.js 5.2.1 core, the `white` theme, the `monokai` highlight theme | cdnjs |
| `reveal/plugin/*.min.js` | the markdown, highlight and notes plugins | cdnjs |
| `fonts/*.woff2` | Open Sans (variable, plus its italic) and Luckiest Guy, latin and latin-ext only | Google Fonts |
| `fonts/fonts.css` | the Google Fonts stylesheet with its `url()`s pointed at the files beside it | Google Fonts |

Open Sans ships as one variable file per subset, so weights 300, 400 and 700 all resolve to the
same `open-sans-normal-*.woff2`; the `@font-face` rules differ only in `font-weight`.

## Licences

All five are permissive and allow redistribution, including in a public repository, as long as
the notice travels with the file. That is what `licenses/` is for; `export.sh` copies the whole
of `vendor/`, so every export carries them too.

| Component | Licence | Text |
|---|---|---|
| reveal.js (core, `white` theme, plugins) | MIT | [licenses/reveal.js-LICENSE](licenses/reveal.js-LICENSE) |
| highlight.js, inside `plugin/highlight.min.js`, and the `monokai` style | BSD 3-Clause | [licenses/highlight.js-LICENSE](licenses/highlight.js-LICENSE) |
| marked, inside `plugin/markdown.min.js` | MIT | [licenses/marked-LICENSE.md](licenses/marked-LICENSE.md) |
| Open Sans | SIL Open Font License 1.1 | [licenses/open-sans-OFL.txt](licenses/open-sans-OFL.txt) |
| Luckiest Guy | Apache License 2.0 | [licenses/luckiest-guy-LICENSE.txt](licenses/luckiest-guy-LICENSE.txt) |

cdnjs strips the licence banners when it minifies, so none of the files says any of this itself.
The texts above come from each project's own repository.

The font files are Google's own subsets, taken as served and not re-subset here, so nothing under
the OFL has been modified and its reserved-name clause does not come into play. Neither licence
is affected by the deck being served from a website.

## Refreshing

To move to another reveal.js version, change `REVEAL` below and re-run it from the deck directory:

```sh
REVEAL=5.2.1
base=https://cdnjs.cloudflare.com/ajax/libs/reveal.js/$REVEAL
curl -sS -o vendor/reveal/reset.min.css    "$base/reset.min.css"
curl -sS -o vendor/reveal/reveal.min.css   "$base/reveal.min.css"
curl -sS -o vendor/reveal/white.min.css    "$base/theme/white.min.css"
curl -sS -o vendor/reveal/monokai.min.css  "$base/plugin/highlight/monokai.min.css"
curl -sS -o vendor/reveal/reveal.min.js    "$base/reveal.min.js"
for p in markdown highlight notes; do
  curl -sS -o "vendor/reveal/plugin/$p.min.js" "$base/plugin/$p/$p.min.js"
done
```

The fonts change only if the deck asks for different families or weights. Fetch the stylesheet
with a current browser's User-Agent (Google serves woff2 only to those), keep the `latin` and
`latin-ext` faces, download each `url()` next to `fonts.css` and rewrite it to the bare filename.

After either, check that nothing reaches outward again:

```sh
grep -r "https\?://" index.html vendor --include='*.css' --include='*.html' | grep -v w3.org
```
