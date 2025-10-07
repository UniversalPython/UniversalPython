#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
from bs4 import BeautifulSoup

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}

def is_relative_url(url: str) -> bool:
    """Return True if the URL is relative (e.g. './file', 'docs/file', etc.)."""
    if not url or url.startswith('#'):
        return False
    return not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url)

def add_raw_true_if_image(url: str) -> str:
    """Append ?raw=true to image-like URLs if not already present."""
    parsed = urlparse(url)
    path_lower = parsed.path.lower()

    if any(path_lower.endswith(ext) for ext in IMAGE_EXTENSIONS):
        query = dict(parse_qsl(parsed.query))
        if 'raw' not in query:
            query['raw'] = 'true'
            parsed = parsed._replace(query=urlencode(query))
    return urlunparse(parsed)

def fix_markdown_links(content: str, base_url: str) -> str:
    """Fix relative Markdown image and normal links."""

    def fix_image(m):
        alt_text, url = m.group(1), m.group(2).strip()
        if is_relative_url(url):
            url = urljoin(base_url + '/', url)
        url = add_raw_true_if_image(url)
        return f'![{alt_text}]({url})'

    def fix_link(m):
        text, url = m.group(1), m.group(2).strip()
        if is_relative_url(url):
            url = urljoin(base_url + '/', url)
        url = add_raw_true_if_image(url)
        return f'[{text}]({url})'

    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_image, content)
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', fix_link, content)
    return content

def fix_html_links(content: str, base_url: str) -> str:
    """Fix relative HTML <img src="..."> and <a href="..."> links."""
    soup = BeautifulSoup(content, 'html.parser')

    # Fix <img src="">
    for img in soup.find_all('img', src=True):
        src = img['src'].strip()
        if is_relative_url(src):
            src = urljoin(base_url + '/', src)
        img['src'] = add_raw_true_if_image(src)

    # Fix <a href="">
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if is_relative_url(href):
            href = urljoin(base_url + '/', href)
        a['href'] = add_raw_true_if_image(href)

    return str(soup)

def fix_readme_links(base_url: str, input_file: Path, inplace: bool = False):
    content = input_file.read_text(encoding='utf-8')

    # 1. Fix HTML links first
    content = fix_html_links(content, base_url)

    # 2. Then fix Markdown links
    content = fix_markdown_links(content, base_url)

    if inplace:
        input_file.write_text(content, encoding='utf-8')
    else:
        sys.stdout.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_readme_links.py BASE_URL README.md [--inplace]", file=sys.stderr)
        sys.exit(1)

    base_url = sys.argv[1].rstrip('/')
    file_path = Path(sys.argv[2])
    inplace = '--inplace' in sys.argv
    fix_readme_links(base_url, file_path, inplace)
