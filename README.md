# morling.dev

This repo contains the source code of the [morling.dev](morling.dev) website.
It is built using [Hugo](https://gohugo.io/) and hosted on [GitHub Pages](https://pages.github.com/).

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
