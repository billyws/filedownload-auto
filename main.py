import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configuration
TARGET_URL = "https://www.nso.gov.pg/documents/"  # Replace with the URL you want to download documents from
DOCUMENT_EXTENSIONS = ['.pdf', '.docx', '.xlsx']  # Add or remove extensions as needed
save_dir = "./Documents"  # Local directory to save downloaded documents

visited_urls = set()  # Track visited URLs to avoid processing a page more than once
document_urls = set()  # Track document URLs to avoid duplicates

def is_valid_url(url, base_url):
    """Check if a URL is valid and belongs to the same domain as the base URL."""
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)
    return bool(parsed.netloc) and bool(parsed.scheme) and parsed.netloc == base_parsed.netloc

def is_document_link(url):
    """Check if a URL is a link to a document based on its extension."""
    return any(url.endswith(ext) for ext in DOCUMENT_EXTENSIONS)

def get_links(url):
    """Fetch the webpage content and parse it for all links."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if is_valid_url(full_url, url):
                yield full_url
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")

def crawl(url):
    """Recursively crawl through the website starting from the given URL."""
    if url in visited_urls:
        return
    print(f"Crawling: {url}")
    visited_urls.add(url)
    for link in get_links(url):
        if is_document_link(link):
            document_urls.add(link)
        elif link not in visited_urls:
            crawl(link)

def download_and_save_file(url):
    """Download a file from a URL and save it to a local directory."""
    local_filename = url.split('/')[-1]
    path = os.path.join(save_dir, local_filename)
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {local_filename} successfully.")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    os.makedirs(save_dir, exist_ok=True)  # Create save directory if it doesn't exist
    crawl(TARGET_URL)  # Start crawling from the target URL

    for doc_url in document_urls:
        download_and_save_file(doc_url)

if __name__ == "__main__":
    main()
