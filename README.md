# morling.dev

This repo contains the source code of the [morling.dev](https://morling.dev) website.
It is built using [Hugo](https://gohugo.io/) and hosted on [GitHub Pages](https://pages.github.com/).

## Set-up

Have Hugo and AsciiDoctor installed, e.g. using Brew on macOS:

```shell
brew install hugo
brew install asciidoctor
```

Clone the repo, including the template sub-module:

```shell
git clone git@github.com:gunnarmorling/morling.dev.git  --recurse-submodules
```

## Editing

Launch a local Hugo server including live reload by running (append `-F` for including future posts):

```
hugo server -D --debug
```

## Deployment

Deployment to GitHub pages happens automatically upon pushing the master branch to the upstream repository by means of a GitHub Action.

In order to deploy to GitHub pages manually, commit all changes, then run:

```
./publish_to_ghpages.sh && git push upstream gh-pages
```
