import requests
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class DeepDarkCTIPuller:
    """
    Fetches raw markdown lists of dark web sources from the deepdarkCTI repository.
    Extracts .onion URLs to be used as seeds for the crawling engine.
    """
    def __init__(self):
        # Base raw URL for the deepdarkCTI repository
        # Targeting specific files that contain onion links, e.g., ransomware leak sites or forums
        self.raw_urls = [
            "https://raw.githubusercontent.com/fastfire/deepdarkCTI/main/ransomware_group.md",
            "https://raw.githubusercontent.com/fastfire/deepdarkCTI/main/forum.md"
        ]
        
    def fetch_raw_markdown(self) -> str:
        """Fetch content from the repository files."""
        combined_content = ""
        for url in self.raw_urls:
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    combined_content += response.text + "\n"
                else:
                    logger.warning(f"Failed to fetch {url} - Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching from deepdarkCTI ({url}): {e}")
        return combined_content

    def extract_onion_links(self, text: str) -> List[str]:
        """Use regex to find standard v3 .onion links in the text."""
        # v3 onion addresses are 56 characters long, base32 encoded
        onion_pattern = r'([a-z2-7]{56}\.onion)'
        links = re.findall(onion_pattern, text)
        
        # Deduplicate and format as full URLs
        unique_links = list(set(links))
        formatted_links = [f"http://{link}" for link in unique_links]
        
        return formatted_links

    def get_seeds(self) -> List[str]:
        """Main execution method to get the final list of seed URLs."""
        logger.info("Starting deepdarkCTI seed extraction...")
        content = self.fetch_raw_markdown()
        seeds = self.extract_onion_links(content)
        logger.info(f"Extracted {len(seeds)} unique onion seeds from deepdarkCTI.")
        return seeds

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    puller = DeepDarkCTIPuller()
    seeds = puller.get_seeds()
    print(f"Found {len(seeds)} seeds. First 5: {seeds[:5]}")
