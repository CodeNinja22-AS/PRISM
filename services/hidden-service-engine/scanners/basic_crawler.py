import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BasicOnionCrawler:
    """
    A lightweight Tor crawler inspired by GDGVIT's Onion Crawler.
    Connects through a local Tor SOCKS5 proxy to scrape basic metadata from hidden services.
    """
    def __init__(self, tor_proxy: str = "socks5h://127.0.0.1:9050"):
        self.proxies = {
            'http': tor_proxy,
            'https': tor_proxy
        }
        # Use a standard user-agent to avoid basic filtering, though advanced sites may block it
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0'
        }
        self.timeout = 30 # Onion routing is slow

    def is_onion_url(self, url: str) -> bool:
        """Validate if the URL is a hidden service."""
        parsed = urlparse(url)
        return parsed.netloc.endswith('.onion')

    def scrape_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to fetch the page and extract basic metadata (Title, headers).
        """
        if not self.is_onion_url(url):
            logger.error(f"Invalid URL. Must be a .onion address: {url}")
            return None

        logger.info(f"Crawling hidden service: {url}")
        
        try:
            # The 'socks5h' scheme tells requests to resolve DNS through the proxy
            # This is critical for .onion domains which don't exist on standard DNS
            response = requests.get(
                url, 
                proxies=self.proxies, 
                headers=self.headers, 
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic metadata
            title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
            
            # Extract outlinks (Breadth-First Search capability)
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if '.onion' in href:
                    links.append(href)
                    
            return {
                "url": url,
                "status_code": response.status_code,
                "title": title,
                "server": response.headers.get('Server', 'Unknown'),
                "content_length": len(response.text),
                "discovered_links": list(set(links)) # Deduplicate
            }
            
        except requests.exceptions.ProxyError:
            logger.error("Proxy Error: Is the Tor service running on 127.0.0.1:9050?")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection Error: The site {url} might be down (common for onions).")
            return None
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = BasicOnionCrawler()
    # Replace with a known active test onion, or a seed from deepdarkCTI
    test_url = "http://expyuz5drlui7sylooyxeqeegce44oewxoyocuimtz75xob4y6qg4pad.onion/" # Example v3
    result = crawler.scrape_metadata(test_url)
    if result:
        print(f"Success! Title: {result['title']}")
