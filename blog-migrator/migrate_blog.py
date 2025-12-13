#!/usr/bin/env python3
"""
Blog migration tool - converts Decodable blog posts to AsciiDoc format for Hugo
"""

import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote
import html2text

def fetch_article(url):
    """Fetch the article HTML from the URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept-Charset': 'utf-8'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # Explicitly set encoding to UTF-8
    response.encoding = 'utf-8'
    return response.text

def extract_article_data(html, url):
    """Extract article metadata and content from HTML"""
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

    # Extract title
    title_elem = soup.find('h1')
    title = title_elem.get_text().strip() if title_elem else 'Untitled'

    # Extract date - Decodable blog specific
    date_str = None

    # Look for date in blog-post-header_meta-wrapper
    meta_wrapper = soup.find('div', class_='blog-post-header_meta-wrapper')
    if meta_wrapper:
        date_text = meta_wrapper.get_text().strip()
        # Extract date pattern like "August 6, 2024"
        date_match = re.search(r'([A-Z][a-z]+\s+\d{1,2},\s+\d{4})', date_text)
        if date_match:
            date_str = date_match.group(1)

    # Also try time element
    if not date_str:
        date_elem = soup.find('time')
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text().strip()

    # Parse date
    article_date = None
    if date_str:
        try:
            # Try various date formats
            for fmt in ['%Y-%m-%d', '%B %d, %Y', '%d %B %Y', '%Y-%m-%dT%H:%M:%S']:
                try:
                    article_date = datetime.strptime(date_str.split('T')[0] if 'T' in date_str else date_str, fmt)
                    break
                except ValueError:
                    continue
        except:
            pass

    if not article_date:
        article_date = datetime.now()

    # Extract main content - Decodable blog specific
    # Look for the rich text content wrapper
    content_elem = soup.find('div', class_='text-rich-text')

    if not content_elem:
        # Fallback to generic selectors
        content_elem = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|post|article', re.I))

    if not content_elem:
        # Last resort: get the body and remove header/footer/nav
        content_elem = soup.find('body')
        if content_elem:
            for tag in content_elem.find_all(['header', 'footer', 'nav', 'aside']):
                tag.decompose()

    return {
        'title': title,
        'date': article_date,
        'content_soup': content_elem,
        'url': url
    }

def download_image(img_url, date, hugo_root):
    """Download an image and save it to the appropriate directory"""
    try:
        # Create directory structure: static/images/YYYY/MM/
        year_month = date.strftime('%Y/%m')
        img_dir = Path(hugo_root) / 'static' / 'images' / year_month
        img_dir.mkdir(parents=True, exist_ok=True)

        # Get the image filename
        parsed_url = urlparse(img_url)
        filename = os.path.basename(parsed_url.path)

        # URL decode the filename to handle %20, %25 etc.
        filename = unquote(filename)

        # Handle query parameters in filename
        if '?' in filename:
            filename = filename.split('?')[0]

        # Ensure we have a valid filename
        if not filename or filename == '':
            filename = 'image.jpg'

        # Download the image
        response = requests.get(img_url, timeout=30)
        response.raise_for_status()

        # Save the image
        img_path = img_dir / filename
        with open(img_path, 'wb') as f:
            f.write(response.content)

        # Return the Hugo path
        return f'/images/{year_month}/{filename}'

    except Exception as e:
        print(f"Warning: Failed to download image {img_url}: {e}")
        return img_url  # Return original URL as fallback

def convert_to_asciidoc(data, hugo_root):
    """Convert HTML content to AsciiDoc format"""
    soup = data['content_soup']
    if not soup:
        return "Content not found"

    # First, decode any HTML-escaped entities in the soup
    # The Decodable blog has escaped inline-code spans
    import html
    html_content = str(soup)
    html_content = html.unescape(html_content)
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')

    asciidoc_lines = []

    def process_element(elem, depth=0):
        """Recursively process HTML elements and convert to AsciiDoc"""
        if elem.name is None:
            # Text node - properly handle encoding
            text = str(elem)
            # Don't strip here - preserve whitespace
            return text

        result = []

        # Handle different HTML elements
        if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(elem.name[1])
            prefix = '=' * (level + 1)  # h1 = ==, h2 = ===, etc.
            text = elem.get_text().strip()
            if text:
                result.append(f'\n{prefix} {text}\n')

        elif elem.name == 'p':
            text = ''
            for child in elem.children:
                text += process_element(child, depth + 1)
            if text.strip():
                result.append(f'{text.strip()}\n\n')

        elif elem.name == 'pre':
            # Code block - check for language
            code_elem = elem.find('code')
            if code_elem:
                # Try to detect language from class
                lang = ''
                classes = code_elem.get('class', [])
                for cls in classes:
                    if cls.startswith('language-'):
                        lang = cls.replace('language-', '')
                        break
                    elif cls in ['sql', 'yaml', 'bash', 'python', 'java', 'javascript', 'json', 'shell']:
                        lang = cls
                        break

                code = code_elem.get_text()
                # Ensure code ends with newline before closing delimiter
                if not code.endswith('\n'):
                    code += '\n'
                result.append(f'\n[source,{lang}]\n----\n{code}----\n')
            else:
                code = elem.get_text()
                # Ensure code ends with newline before closing delimiter
                if not code.endswith('\n'):
                    code += '\n'
                result.append(f'\n[source]\n----\n{code}----\n')

        elif elem.name == 'code' and elem.parent.name != 'pre':
            # Inline code
            return f'`{elem.get_text()}`'

        elif elem.name == 'span' and 'inline-code' in elem.get('class', []):
            # Decodable blog uses span.inline-code for inline code
            return f'`{elem.get_text()}`'

        elif elem.name == 'blockquote':
            text = ''
            for child in elem.children:
                text += process_element(child, depth + 1)
            if text.strip():
                # AsciiDoc blockquote
                quoted = '\n'.join([f'> {line}' if line else '>' for line in text.strip().split('\n')])
                result.append(f'\n{quoted}\n')

        elif elem.name in ['ul', 'ol']:
            for li in elem.find_all('li', recursive=False):
                prefix = '*' if elem.name == 'ul' else '.'
                text = ''
                for child in li.children:
                    if child.name in ['ul', 'ol']:
                        continue  # Handle nested lists separately
                    text += process_element(child, depth + 1)
                if text.strip():
                    result.append(f'{prefix} {text.strip()}\n')

                # Handle nested lists
                for nested in li.find_all(['ul', 'ol'], recursive=False):
                    nested_result = process_element(nested, depth + 1)
                    result.append(nested_result)

            # Add blank line after list ends
            result.append('\n')

        elif elem.name == 'img':
            img_url = elem.get('src', '')
            alt_text = elem.get('alt', '')

            # Make URL absolute if relative
            if img_url and not img_url.startswith('http'):
                img_url = urljoin(data['url'], img_url)

            # Download image
            if img_url:
                local_path = download_image(img_url, data['date'], hugo_root)
                result.append(f'\nimage::{local_path}[{alt_text}]\n')

        elif elem.name == 'a':
            href = elem.get('href', '')
            text = elem.get_text().strip()
            if href and text:
                result.append(f' link:{href}[{text}] ')
            elif text:
                result.append(text)

        elif elem.name in ['strong', 'b']:
            text = elem.get_text().strip()
            return f'*{text}*'

        elif elem.name in ['em', 'i']:
            text = elem.get_text().strip()
            return f'_{text}_'

        elif elem.name == 'br':
            return ' +\n'

        elif elem.name in ['div', 'section', 'article', 'span']:
            # Process children
            for child in elem.children:
                result.append(process_element(child, depth + 1))

        else:
            # For other elements, process children
            for child in elem.children:
                result.append(process_element(child, depth + 1))

        return ''.join(result)

    # Process the content
    content = process_element(soup)

    # Post-process to fix common encoding issues
    # Fix box-drawing pipe character that should be regular pipe
    content = content.replace('│', '|')
    # Fix zero-width space and other invisible characters
    content = content.replace('\u200b', '')  # zero-width space
    content = content.replace('\u200c', '')  # zero-width non-joiner
    content = content.replace('\u200d', '')  # zero-width joiner
    content = content.replace('\ufeff', '')  # zero-width no-break space

    # Apply One Sentence Per Line (OSPL) formatting
    # Important: In AsciiDoc, paragraphs are separated by blank lines
    lines = content.split('\n')
    formatted_lines = []
    in_code_block = False

    for line in lines:
        # Check if entering/exiting code block
        if line.strip() == '----':
            in_code_block = not in_code_block
            formatted_lines.append(line)
            continue

        # Preserve blank lines (paragraph separators)
        if line.strip() == '':
            formatted_lines.append(line)
            continue

        # Don't format lines that are:
        # - Inside code blocks
        # - Headings (start with =)
        # - List items (start with * or .)
        # - Source directives
        # - Image directives
        if (in_code_block or
            line.startswith('=') or
            line.startswith('*') or
            line.startswith('.') or
            line.startswith('[source') or
            line.startswith('image::') or
            line.startswith('----')):
            formatted_lines.append(line)
        else:
            # Apply OSPL: split on sentence boundaries (. ! ?) followed by space
            # But be careful not to split inside inline code (backticks)
            # And properly handle formatting markers (_ and *)
            sentences = []
            current = ''
            in_backticks = False
            in_italic = False  # Track if we're in italic block
            in_bold = False    # Track if we're in bold block
            skip_next = False

            for i, char in enumerate(line):
                if skip_next:
                    if char != ' ':  # Don't add the space itself
                        current += char
                    skip_next = False
                    continue

                if char == '`':
                    in_backticks = not in_backticks
                    current += char
                elif char == '_' and not in_backticks:
                    in_italic = not in_italic
                    current += char
                elif char == '*' and not in_backticks:
                    in_bold = not in_bold
                    current += char
                elif char in '.!?' and not in_backticks:
                    current += char
                    # Check if followed by space (sentence boundary)
                    if i + 1 < len(line) and line[i + 1] == ' ':
                        # Close any open formatting for this sentence
                        sentence = current.strip()
                        if in_italic and not sentence.endswith('_'):
                            sentence += '_'
                        if in_bold and not sentence.endswith('*'):
                            sentence += '*'
                        sentences.append(sentence)

                        # Start next sentence with formatting markers if needed
                        current = ''
                        if in_italic:
                            current = '_'
                        if in_bold:
                            current = '*'
                        skip_next = True  # Skip the space
                else:
                    current += char

            # Add any remaining text
            if current.strip():
                sentences.append(current.strip())

            # Add sentences as separate lines
            formatted_lines.extend(sentences)

    content = '\n'.join(formatted_lines)

    return content.strip()

def create_hugo_post(data, content, hugo_root):
    """Create the Hugo post file with frontmatter"""
    # Generate filename from title
    slug = re.sub(r'[^\w\s-]', '', data['title'].lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    filename = f"{slug}.adoc"

    # Create the post directory
    post_dir = Path(hugo_root) / 'content' / 'post'
    post_dir.mkdir(parents=True, exist_ok=True)

    post_path = post_dir / filename

    # Create frontmatter
    date_str = data['date'].strftime('%Y-%m-%dT%H:%M:%S%z')
    if not date_str.endswith(('+', '-')):
        date_str += '+00:00'

    # Try to find a header image
    header_image = ''
    year_month = data['date'].strftime('%Y/%m')

    frontmatter = f"""---
title: '{data['title']}'
date: "{date_str}"
draft: true
markup: adoc
canonical_url: {data['url']}
---
:source-highlighter: rouge
:rouge-style: base16.dark
:icons: font
:imagesdir: /images
ifdef::env-github[]
:imagesdir: ../../static/images
endif::[]

_This post originally appeared on the link:{data['url']}[Decodable blog]._

"""

    # Add <!--more--> after the first paragraph
    # Split content into lines and find the first blank line (end of first paragraph)
    content_lines = content.split('\n')
    modified_lines = []
    first_blank_found = False

    for i, line in enumerate(content_lines):
        modified_lines.append(line)
        if not first_blank_found and line.strip() == '' and i > 0:
            # Found the first blank line after some content
            modified_lines.append('<!--more-->')
            first_blank_found = True

    content_with_more = '\n'.join(modified_lines)

    # Combine frontmatter and content
    full_content = frontmatter + content_with_more

    # Write the file
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"Created post: {post_path}")
    return post_path

def commit_article(post_path, data, hugo_root):
    """Commit the article and its images to git"""
    import subprocess

    # Change to hugo root directory
    original_dir = os.getcwd()
    os.chdir(hugo_root)

    try:
        # Get the year/month for images
        year_month = data['date'].strftime('%Y/%m')
        images_path = f"static/images/{year_month}"

        # Stage the post file
        subprocess.run(['git', 'add', str(post_path)], check=True)

        # Stage images if they exist
        if os.path.exists(images_path):
            subprocess.run(['git', 'add', images_path], check=True)

        # Create commit message
        commit_msg = f"""Migrate: {data['title']}

Source: {data['url']}
Date: {data['date'].strftime('%Y-%m-%d')}

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"""

        # Commit
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print(f"✓ Committed: {data['title']}")

    except subprocess.CalledProcessError as e:
        print(f"Warning: Git commit failed: {e}")
    finally:
        os.chdir(original_dir)

def main():
    # Configuration
    urls_file = '/Users/gunnarmorling/Development/website/morling.dev/blog-migrator/urls.txt'
    hugo_root = '/Users/gunnarmorling/Development/website/morling.dev'

    # Read URLs
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(urls)} article(s)...")

    for url in urls:
        print(f"\nProcessing: {url}")

        try:
            # Fetch article
            html = fetch_article(url)

            # Extract data
            data = extract_article_data(html, url)
            print(f"Title: {data['title']}")
            print(f"Date: {data['date'].strftime('%Y-%m-%d')}")

            # Convert to AsciiDoc
            content = convert_to_asciidoc(data, hugo_root)

            # Create Hugo post
            post_path = create_hugo_post(data, content, hugo_root)

            print(f"✓ Successfully migrated to {post_path}")

            # Commit the article
            # commit_article(post_path, data, hugo_root)

        except Exception as e:
            print(f"✗ Error processing {url}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
