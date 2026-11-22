#!/usr/bin/env python3
import os
import re
from pathlib import Path

blog_dir = Path("/app/content/blog")
posts_with_multiple_tags = []

for post_file in sorted(blog_dir.glob("*.asciidoc")):
    with open(post_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract front matter (between --- markers)
    front_matter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)

    if not front_matter_match:
        continue

    front_matter = front_matter_match.group(1)

    # Find all lines that start with "tags:"
    tag_lines = re.findall(r'^tags:\s*(.*)$', front_matter, re.MULTILINE)

    # Also check for other tag-related fields
    all_tag_fields = re.findall(r'^(tags|tag|categories|category):\s*(.*)$', front_matter, re.MULTILINE)

    # Check if there are multiple "tags:" lines specifically
    if len(tag_lines) > 1:
        posts_with_multiple_tags.append({
            'file': post_file.name,
            'tag_lines': tag_lines,
            'all_fields': all_tag_fields
        })
        print(f"\n{'='*80}")
        print(f"File: {post_file.name}")
        print(f"Found {len(tag_lines)} 'tags:' lines in front matter:")
        for i, line in enumerate(tag_lines, 1):
            print(f"  {i}. tags: {line}")

        # Also show any other tag-related fields
        other_fields = [f for f in all_tag_fields if f[0] != 'tags']
        if other_fields:
            print(f"Other tag-related fields:")
            for field, value in other_fields:
                print(f"  - {field}: {value}")

if not posts_with_multiple_tags:
    print("No posts found with multiple 'tags:' fields in front matter.")
else:
    print(f"\n{'='*80}")
    print(f"\nTotal posts with multiple tags fields: {len(posts_with_multiple_tags)}")
