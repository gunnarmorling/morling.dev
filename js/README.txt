JavaScript Files Location
=========================

Location:
---------
JavaScript source files are located in different directories:

Processed files (minified via Hugo Pipes):
  - /themes/ezhil/assets/js/main.js

Already minified files (served as-is):
  - /themes/ezhil/static/js/medium-zoom.min.js

Why:
----
main.js is processed through Hugo Pipes (resources.Get) which:
1. Minifies the JavaScript
2. Adds fingerprinting (cache-busting via content hash)
3. Serves optimized file from /resources/ directory

medium-zoom.min.js is already pre-minified and stays in static/js/
since it doesn't need further processing.

To update JavaScript:
---------------------
- For main.js: Edit /themes/ezhil/assets/js/main.js and rebuild with Hugo
- For medium-zoom.min.js: Replace file in /themes/ezhil/static/js/
