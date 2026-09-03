import logging
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SeleniumTorCrawler:
    """
    DARC-inspired crawler using Selenium to render JavaScript-heavy hidden services.
    Uses Firefox geckodriver routed through the local Tor SOCKS proxy.
    """
    def __init__(self, proxy_host: str = "127.0.0.1", proxy_port: int = 9050, headless: bool = True):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.headless = headless

    def get_driver(self) -> webdriver.Firefox:
        options = Options()
        if self.headless:
            options.add_argument("--headless")

        # Configure Firefox to use Tor proxy
        options.set_preference('network.proxy.type', 1)
        options.set_preference('network.proxy.socks', self.proxy_host)
        options.set_preference('network.proxy.socks_port', self.proxy_port)
        options.set_preference('network.proxy.socks_remote_dns', True)
        
        # Disable webrtc to prevent IP leaks
        options.set_preference('media.peerconnection.enabled', False)
        
        # Start driver (Requires geckodriver in PATH)
        try:
            driver = webdriver.Firefox(options=options)
            driver.set_page_load_timeout(60) # Tor is slow
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Firefox WebDriver: {e}")
            raise

    def scrape_dynamic_page(self, url: str) -> Optional[str]:
        """Loads a page with JS execution and returns the fully rendered DOM source."""
        parsed = urlparse(url)
        if not parsed.netloc.endswith('.onion'):
            logger.error("URL must be an .onion address")
            return None

        driver = None
        try:
            driver = self.get_driver()
            logger.info(f"Loading {url} via Selenium...")
            driver.get(url)
            
            # Wait for potential JS to execute (e.g. anti-DDoS checks like Dread's CAPTCHA page)
            time.sleep(5) 
            
            # Here we could add logic to detect standard CAPTCHAs and alert an operator
            if "captcha" in driver.page_source.lower():
                logger.warning(f"CAPTCHA detected on {url}. Manual intervention may be required.")
            
            return driver.page_source

        except Exception as e:
            logger.error(f"Selenium crawling failed for {url}: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = SeleniumTorCrawler()
    # Test with Tor check to ensure it's routing through Tor
    source = crawler.scrape_dynamic_page("https://check.torproject.org/")
    if source and "Congratulations" in source:
        print("Successfully routed Selenium through Tor!")
    else:
        print("Failed to route Selenium through Tor.")
