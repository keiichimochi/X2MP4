import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import gzip
from io import BytesIO
import html2text

def get_sitemap(url):
    try:
        # If the URL doesn't end with .xml, try to find the sitemap
        if not url.endswith('.xml'):
            url = find_sitemap_url(url)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Check if the content is gzipped
        if response.headers.get('Content-Type') == 'application/x-gzip':
            content = gzip.decompress(response.content)
        else:
            content = response.content

        # Try parsing as XML first
        try:
            soup = BeautifulSoup(content, 'xml')
            urls = [loc.text for loc in soup.find_all('loc')]
            if not urls:
                # Check if it's a sitemap index
                sitemaps = soup.find_all('sitemap')
                if sitemaps:
                    urls = []
                    for sitemap in sitemaps:
                        sitemap_url = sitemap.find('loc').text
                        urls.extend(get_sitemap(sitemap_url))
        except:
            # If XML parsing fails, try parsing as text
            urls = [line.strip() for line in content.decode().splitlines() if line.strip().startswith('http')]
        
        return urls
    except Exception as e:
        st.error(f"Error fetching sitemap: {e}")
        return []

def find_sitemap_url(base_url):
    common_sitemap_paths = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap/',
        '/sitemap/sitemap.xml',
    ]
    
    for path in common_sitemap_paths:
        sitemap_url = urljoin(base_url, path)
        try:
            response = requests.head(sitemap_url)
            if response.status_code == 200:
                return sitemap_url
        except:
            pass
    
    # If no sitemap is found, try to parse robots.txt
    robots_url = urljoin(base_url, '/robots.txt')
    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.lower().startswith('sitemap:'):
                    return line.split(':', 1)[1].strip()
    except:
        pass
    
    # If still no sitemap is found, return the original URL
    return base_url

def build_tree(urls):
    tree = lambda: defaultdict(tree)
    root = tree()
    for url in urls:
        parsed = urlparse(url)
        parts = [parsed.netloc] + parsed.path.strip('/').split('/')
        current = root
        for part in parts:
            current = current[part]
    return root

def display_tree(tree, level=0):
    for key, subtree in tree.items():
        st.text('  ' * level + f"- {key}")
        if level < 5:  # Limit depth to prevent excessive nesting
            display_tree(subtree, level + 1)

def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # タイトルを取得
        title = soup.title.string if soup.title else "No Title"
        
        # メインコンテンツを取得 (この部分はウェブサイトの構造に応じて調整が必要)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            # HTMLをMarkdownに変換
            html = str(main_content)
            text = html2text.html2text(html)
        else:
            text = "Content not found"
        
        return f"# {title}\n\n{text}\n\n"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}\n\n"

def create_markdown_file(urls):
    markdown_content = ""
    for url in urls:
        markdown_content += scrape_page(url)
    return markdown_content

st.title("Website to Markdown Scraper")
url = st.text_input("Enter the URL of the website or sitemap (e.g., https://example.com or https://example.com/sitemap.xml)")

if st.button("Scrape and Create Markdown"):
    if url:
        with st.spinner("Fetching sitemap..."):
            urls = get_sitemap(url)
        if urls:
            st.success(f"Found {len(urls)} pages.")
            with st.spinner("Scraping pages and creating Markdown..."):
                markdown_content = create_markdown_file(urls)
                st.download_button(
                    label="Download Markdown File",
                    data=markdown_content,
                    file_name="scraped_content.md",
                    mime="text/markdown"
                )
        else:
            st.warning("No URLs found in the sitemap. The site might not have a public sitemap or it might be protected.")
    else:
        st.error("Please enter a valid URL.")