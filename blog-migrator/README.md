# Blog Migration Tool

This tool migrates blog posts from Decodable to AsciiDoc format for Hugo.

## Features

- Converts HTML blog posts to AsciiDoc format
- Downloads and organizes images by date (YYYY/MM structure)
- Preserves formatting:
  - Code blocks with syntax highlighting
  - Headings hierarchy
  - Links and inline code
  - Blockquotes
  - Lists (ordered and unordered)
  - Bold and italic text
- Handles Decodable blog-specific formatting (inline-code spans)
- HTML entity decoding

## Setup

1. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install beautifulsoup4 requests html2text
   ```

2. Add URLs to `urls.txt` (one per line)

## Usage

```bash
source .venv/bin/activate
python3 migrate_blog.py
```

The script will:
- Read URLs from `urls.txt`
- Fetch each article
- Convert to AsciiDoc
- Download images to `~/git/rmoff-blog/static/images/YYYY/MM/`
- Save posts to `~/git/rmoff-blog/content/post/`

## Configuration

Edit `migrate_blog.py` to change:
- `urls_file`: Path to URL list (default: `urls.txt`)
- `hugo_root`: Path to Hugo blog root (default: `~/git/rmoff-blog`)

## Output Format

Generated posts include Hugo frontmatter:
```yaml
---
title: 'Post Title'
date: "YYYY-MM-DDTHH:MM:SS+00:00"
draft: false
credit: "https://bsky.app/profile/rmoff.net"
categories:
- Apache Flink
---

NOTE: This post originally appeared on the link:https://www.decodable.co/blog/...[Decodable blog].
```

## Formatting

- **OSPL (One Sentence Per Line)**: Each sentence is on its own line
- **Blank lines**: Separate paragraphs and follow lists
- **Italic/Bold**: Formatting markers properly closed/opened on each line when sentences are split
- **Inline code**: Never split across lines
- **Code blocks**: Properly delimited with `----` on separate lines

## Notes

- All posts are categorized as "Apache Flink"
- Each post includes a NOTE header linking to the original Decodable blog post
- Images are downloaded to maintain local copies
- The script preserves the original article date from the source
- Branch: Work in a separate git branch for safety
