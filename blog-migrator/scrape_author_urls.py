#!/usr/bin/env python3
"""
Scrape all blog post URLs from a Decodable author page
Handles the "Load more" button to get all posts
"""

import requests
from bs4 import BeautifulSoup
import time
import re

def scrape_author_page(author_url, output_file='urls.txt'):
    """
    Scrape all blog post URLs from a Decodable author page
    Note: This fetches the initial page. For full pagination, you'd need Selenium
    to click "Load more" buttons. This version extracts visible posts.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    print(f"Fetching author page: {author_url}")
    response = requests.get(author_url, headers=headers)
    response.encoding = 'utf-8'
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all blog post links
    # Decodable blog posts are in the format: /blog/post-title
    blog_links = set()

    # Look for links that match the blog post pattern
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Match /blog/something but not /blog/author or /blog/category
        if '/blog/' in href and '/blog/author' not in href and '/blog/category' not in href:
            # Make absolute URL
            if href.startswith('/'):
                full_url = f"https://www.decodable.co{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                continue

            # Only include actual blog posts (not just /blog)
            if full_url != 'https://www.decodable.co/blog' and full_url != 'https://www.decodable.co/blog/':
                blog_links.add(full_url)

    # Sort URLs for consistent output
    sorted_urls = sorted(blog_links)

    print(f"\nFound {len(sorted_urls)} blog posts")

    # Write to file
    with open(output_file, 'w') as f:
        for url in sorted_urls:
            f.write(f"{url}\n")

    print(f"URLs written to {output_file}")

    # Print first few URLs as preview
    print("\nFirst 5 URLs:")
    for url in sorted_urls[:5]:
        print(f"  {url}")

    if len(sorted_urls) > 5:
        print(f"  ... and {len(sorted_urls) - 5} more")

    return sorted_urls

def scrape_with_selenium(author_url, output_file='urls.txt'):
    """
    Alternative method using Selenium to handle "Load more" button
    Requires: pip install selenium
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
    except ImportError:
        print("Selenium not installed. Using basic scraper instead.")
        print("For full pagination support, install: pip install selenium")
        return scrape_author_page(author_url, output_file)

    print(f"Using Selenium to fetch all posts from: {author_url}")

    # Setup Chrome in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(author_url)

    # Click "Load more" button until all posts are loaded
    clicks = 0
    max_clicks = 20  # Safety limit
    while clicks < max_clicks:
        try:
            # Wait a bit for content to load
            time.sleep(2)

            # Try to find "Load more" button by class
            load_more = driver.find_element(By.CSS_SELECTOR, "a.w-pagination-next")

            if load_more and load_more.is_displayed():
                print(f"Clicking 'Load more' button (click {clicks + 1})...")
                driver.execute_script("arguments[0].scrollIntoView();", load_more)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", load_more)
                clicks += 1
                time.sleep(3)  # Wait for new content to load
            else:
                break
        except (NoSuchElementException, TimeoutException):
            print(f"No more 'Load more' button found after {clicks} clicks")
            break

    # Get page source and parse
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Extract URLs (same logic as above)
    blog_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/blog/' in href and '/blog/author' not in href and '/blog/category' not in href:
            if href.startswith('/'):
                full_url = f"https://www.decodable.co{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                continue

            if full_url != 'https://www.decodable.co/blog' and full_url != 'https://www.decodable.co/blog/':
                blog_links.add(full_url)

    sorted_urls = sorted(blog_links)
    print(f"\nFound {len(sorted_urls)} blog posts")

    with open(output_file, 'w') as f:
        for url in sorted_urls:
            f.write(f"{url}\n")

    print(f"URLs written to {output_file}")
    return sorted_urls

if __name__ == '__main__':
    author_url = "https://www.decodable.co/blog-author/gunnar-morling"
    output_file = "urls.txt"

    print("Choose scraping method:")
    print("1. Basic scraper (fast, may miss posts behind 'Load more')")
    print("2. Selenium scraper (complete, requires selenium and chromedriver)")

    choice = input("Enter choice (1 or 2, default=2): ").strip() or "2"

    if choice == "2":
        scrape_with_selenium(author_url, output_file)
    else:
        scrape_author_page(author_url, output_file)
