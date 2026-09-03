import requests
from bs4 import BeautifulSoup
import logging
from stem import Signal
from stem.control import Controller
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class AdvancedTorCrawler:
    """
    Advanced Tor crawler inspired by TorBot.
    Features Tor circuit rotation via Stem to avoid IP bans when scraping heavily guarded dark web forums.
    """
    def __init__(self, proxy_port: int = 9050, control_port: int = 9051, control_password: str = ""):
        self.proxies = {
            'http': f'socks5h://127.0.0.1:{proxy_port}',
            'https': f'socks5h://127.0.0.1:{proxy_port}'
        }
        self.control_port = control_port
        self.control_password = control_password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0'
        }
        self.timeout = 45

    def rotate_ip(self):
        """Signals the local Tor instance to build a new circuit, effectively changing the exit IP."""
        logger.info("Requesting new Tor circuit (IP rotation)...")
        try:
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate(password=self.control_password)
                controller.signal(Signal.NEWNYM)
                time.sleep(5) # Give Tor time to build the new circuit
                logger.info("Tor circuit rotated successfully.")
        except Exception as e:
            logger.error(f"Failed to rotate Tor circuit: {e}. Is the control port open in torrc?")

    def check_current_ip(self) -> str:
        """Utility to verify the current IP address through the Tor proxy."""
        try:
            r = requests.get('https://check.torproject.org/api/ip', proxies=self.proxies, timeout=15)
            return r.json().get('IP', 'Unknown')
        except Exception:
            return "Unknown"

    def fetch_page(self, url: str, attempt: int = 1, max_attempts: int = 3) -> Optional[str]:
        """Fetches a page, rotating the IP if a block (e.g., 403, 429) is detected."""
        if attempt > max_attempts:
            logger.error(f"Max attempts reached for {url}")
            return None
            
        try:
            response = requests.get(url, proxies=self.proxies, headers=self.headers, timeout=self.timeout)
            
            # Anti-bot detection
            if response.status_code in [403, 429, 503]:
                logger.warning(f"Blocked (Status {response.status_code}) on {url}. Rotating IP and retrying...")
                self.rotate_ip()
                return self.fetch_page(url, attempt + 1, max_attempts)
                
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None

    def scrape_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        parsed = urlparse(url)
        if not parsed.netloc.endswith('.onion'):
            return None

        html_content = self.fetch_page(url)
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '.onion' in href:
                links.append(href)
                
        return {
            "url": url,
            "title": title,
            "content_length": len(html_content),
            "discovered_links": list(set(links)),
            "raw_html": html_content
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = AdvancedTorCrawler()
    print(f"Current Tor Exit IP: {crawler.check_current_ip()}")
    crawler.rotate_ip()
    print(f"New Tor Exit IP: {crawler.check_current_ip()}")
