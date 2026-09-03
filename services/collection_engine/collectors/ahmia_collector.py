import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any
from .base import BaseCollector

logger = logging.getLogger(__name__)

class AhmiaCollector(BaseCollector):
    """
    Queries Ahmia's clearnet search engine for a given target keyword to find relevant .onion links.
    """
    def __init__(self, target_keyword: str):
        super().__init__(source_id="ahmia_search")
        self.target = target_keyword
        self.search_url = "https://ahmia.fi/search/"

    def fetch_data(self) -> Any:
        try:
            params = {"q": self.target}
            response = requests.get(self.search_url, params=params, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch data from Ahmia: {e}")
            return ""

    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        evidence = []
        if not raw_data:
            return evidence

        soup = BeautifulSoup(raw_data, 'html.parser')
        
        # Ahmia search results are generally inside <li> tags with class "result"
        results = soup.find_all('li', class_='result')
        
        for res in results:
            try:
                # Find the cite tag which contains the onion url
                cite_tag = res.find('cite')
                if cite_tag:
                    onion_url = cite_tag.text.strip()
                    if ".onion" in onion_url:
                        evidence.append({
                            "type": "darkweb_mention",
                            "value": onion_url,
                            "confidence": 0.85,  # High confidence it's an onion link, medium that it's highly relevant
                            "source": "Ahmia",
                            "raw_context": res.text.strip()[:200] # Snippet
                        })
            except Exception as e:
                logger.debug(f"Error parsing Ahmia result: {e}")
                
        return evidence
