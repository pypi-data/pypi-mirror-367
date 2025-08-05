import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import shutil
import time
from abstract_webtools import *


# Import your custom classes/functions
# from your_module import linkManager, get_soup_mgr

# Configuration
def normalize_url(url, base_url):
    """
    Normalize and resolve relative URLs, ensuring proper domain and format.
    """
    # If URL starts with the base URL repeated, remove the extra part
    if url.startswith(base_url):
        url = url[len(base_url):]

    # Resolve the URL against the base URL
    normalized_url = urljoin(base_url, url.split('#')[0])

    # Ensure only URLs belonging to the base domain are kept
    if not normalized_url.startswith(base_url):
        return None

    return normalized_url


def is_valid_url(url, base_domain):
    """
    Check if the URL is valid and belongs to the same domain.
    """
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and parsed.netloc == base_domain
def save_page(url, content,output_dir):
    """
    Save HTML page to local directory.
    """
    parsed_url = urlparse(url)
    page_path = parsed_url.path.lstrip('/')

    if not page_path or page_path.endswith('/'):
        page_path = os.path.join(page_path, 'index.html')
    elif not os.path.splitext(page_path)[1]:
        page_path += '.html'

    page_full_path = os.path.join(output_dir, page_path)
    os.makedirs(os.path.dirname(page_full_path), exist_ok=True)

    with open(page_full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved page: {page_full_path}")
def save_asset(asset_url, base_url,output_dir,session):
    """
    Download and save assets like images, CSS, JS files.
    """
    asset_url = normalize_url(asset_url, base_url)
    if asset_url in downloaded_assets:
        return
    downloaded_assets.add(asset_url)

    parsed_url = urlparse(asset_url)
    asset_path = parsed_url.path.lstrip('/')
    if not asset_path:
        return  # Skip if asset path is empty

    asset_full_path = os.path.join(output_dir, asset_path)
    os.makedirs(os.path.dirname(asset_full_path), exist_ok=True)

    try:
        response = session.get(asset_url, stream=True)
        response.raise_for_status()
        with open(asset_full_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Saved asset: {asset_full_path}")
    except Exception as e:
        print(f"Failed to save asset {asset_url}: {e}")
class usurpManager():
    def __init__(self,url,output_dir=None,max_depth=None,wait_between_requests=None,operating_system=None, browser=None, version=None,user_agent=None,website_bot=None):
        self.url = url
        website_bot = website_bot or 'http://yourwebsite.com/bot'
        self.user_agent_mgr = UserAgentManager(operating_system=operating_system,browser=browser,version=version,user_agent=user_agent)
        self.BASE_URL = urlManager(url=self.url).url  # Replace with your website's URL
        self.OUTPUT_DIR = output_dir or 'download_site'
        self.MAX_DEPTH = max_depth or 5  # Adjust as needed
        self.WAIT_BETWEEN_REQUESTS = wait_between_requests or 1  # Seconds to wait between requests
        USER_AGENT = self.user_agent_mgr.get_user_agent()
        self.USER_AGENT = f"{USER_AGENT};{website_bot})"  # Customize as needed
        # Initialize global sets
        self.visited_pages = set()
        self.downloaded_assets = set()

        # Session with custom headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-US,en;q=0.5',
            "Access-Control-Allow-Origin": "*"})

    def process_page(self,url, depth, base_domain):
        """
        Process a single page: download assets, save HTML, and crawl links.
        """
        print(url)
        if url in self.visited_pages or depth > self.MAX_DEPTH:
            return
        self.visited_pages.add(url)
        
        try:
            # Fetch the page content
            response = self.session.get(url)
            response.raise_for_status()
            content = response.text

            # Use your get_soup_mgr function to get the soup and attributes
            soup_mgr = get_soup_mgr(url=url)
            soup = soup_mgr.soup
            all_attributes = soup_mgr.get_all_attribute_values()
            # Now you can use all_attributes as needed

            # Update asset links to local paths
            for tag in soup.find_all(['img', 'script', 'link']):
                attr = 'src' if tag.name != 'link' else 'href'
                asset_url = tag.get(attr)
                if asset_url:
                    full_asset_url = normalize_url(asset_url, url)
                    parsed_asset_url = urlparse(full_asset_url)

                    if is_valid_url(full_asset_url, base_domain):
                        save_asset(full_asset_url, self.url,self.session)
                        # Update tag to point to the local asset
                        local_asset_path = '/' + parsed_asset_url.path.lstrip('/')
                        tag[attr] = local_asset_path

            # Save the modified page
            save_page(url, str(soup),self.OUTPUT_DIR)

            # Use your linkManager to find all domain links
            link_mgr = linkManager(url=url)
            all_domains = link_mgr.find_all_domain()

            # Process each domain link
            for link_url in all_domains:
                normalized_link = normalize_url(link_url, url)
                if is_valid_url(normalized_link, base_domain):
                    time.sleep(self.WAIT_BETWEEN_REQUESTS)
                    self.process_page(normalized_link, depth + 1, base_domain)

        except Exception as e:
            print(f"Failed to process page {url}: {e}")

    def main(self):
        # Ensure output directory exists
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        base_parsed = urlparse(self.BASE_URL)
        base_domain = base_parsed.netloc

        self.process_page(self.BASE_URL, 0, base_domain)
        print("Website copying completed.")
def test_download(url,directory):
    url=url or 'https://algassert.com/quantum/2016/01/07/Delayed-Choice-Quantum-Erasure.html'
    output_dir= directory or os.path.join(os.getcwd(),'testit')
    os.makedirs(output_dir,exist_ok=True)
    site_mgr = usurpManager(url,output_dir)
    site_mgr.main()
