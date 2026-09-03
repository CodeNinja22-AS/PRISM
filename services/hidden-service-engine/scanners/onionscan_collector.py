import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any, List
import ssl
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class OnionScanCollector:
    """
    OnionScan-inspired OpSec scanner for attribution.
    Actively probes hidden services for misconfigurations that leak clearnet infrastructure details.
    """
    def __init__(self, tor_proxy: str = "socks5h://127.0.0.1:9050"):
        self.proxies = {
            'http': tor_proxy,
            'https': tor_proxy
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0'
        }
        self.timeout = 20

    def check_apache_status(self, url: str) -> List[Dict[str, Any]]:
        """
        Probes for exposed /server-status pages which often leak real IPs and internal network paths.
        """
        evidence = []
        target_url = f"{url.rstrip('/')}/server-status"
        logger.info(f"Probing {target_url} for Apache Server Status leak...")
        
        try:
            r = requests.get(target_url, proxies=self.proxies, headers=self.headers, timeout=self.timeout)
            if r.status_code == 200 and "Apache Status" in r.text:
                logger.warning(f"[VULNERABILITY] Exposed server-status found at {target_url}")
                evidence.append({
                    "type": "opsec_failure",
                    "subtype": "apache_server_status",
                    "value": target_url,
                    "confidence": 1.0, # 100% confidence it's an exposed page
                    "criticality": "HIGH",
                    "details": "Exposed Apache server-status page leaking internal infrastructure details."
                })
        except Exception as e:
            logger.debug(f"Server-status probe failed: {e}")
            
        return evidence

    def check_open_directories(self, url: str) -> List[Dict[str, Any]]:
        """
        Probes common open directories that might contain exposed keys or logs.
        """
        evidence = []
        paths = ["/.git/", "/.ssh/", "/backup/", "/logs/"]
        
        for path in paths:
            target_url = f"{url.rstrip('/')}{path}"
            try:
                r = requests.get(target_url, proxies=self.proxies, headers=self.headers, timeout=self.timeout)
                # Apache/Nginx standard directory listing headers
                if r.status_code == 200 and ("Index of /" in r.text or "Directory listing for" in r.text):
                    logger.warning(f"[VULNERABILITY] Open directory found: {target_url}")
                    evidence.append({
                        "type": "opsec_failure",
                        "subtype": "open_directory",
                        "value": target_url,
                        "confidence": 0.9,
                        "criticality": "HIGH",
                        "details": f"Directory {path} is openly accessible."
                    })
            except Exception:
                pass
                
        return evidence
        
    def check_http_headers(self, url: str) -> List[Dict[str, Any]]:
        """
        Analyzes HTTP response headers for unique signatures (e.g., precise server version, custom headers).
        """
        evidence = []
        try:
            r = requests.get(url, proxies=self.proxies, headers=self.headers, timeout=self.timeout)
            server_header = r.headers.get('Server', '')
            
            # If they leak an exact OS and version (e.g., Apache/2.4.41 (Ubuntu))
            if "Ubuntu" in server_header or "Debian" in server_header or "Win32" in server_header:
                evidence.append({
                    "type": "infrastructure_fingerprint",
                    "subtype": "server_version_leak",
                    "value": server_header,
                    "confidence": 0.8,
                    "criticality": "MEDIUM",
                    "details": "Server header leaks underlying OS version, enabling Shodan correlation."
                })
        except Exception:
            pass
            
        return evidence

    def scan_target(self, url: str) -> List[Dict[str, Any]]:
        """
        Run the full suite of OpSec checks against a hidden service.
        """
        logger.info(f"Starting OnionScan attribution checks against {url}")
        all_evidence = []
        
        all_evidence.extend(self.check_apache_status(url))
        all_evidence.extend(self.check_open_directories(url))
        all_evidence.extend(self.check_http_headers(url))
        
        return all_evidence

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scanner = OnionScanCollector()
    test_url = "http://expyuz5drlui7sylooyxeqeegce44oewxoyocuimtz75xob4y6qg4pad.onion"
    results = scanner.scan_target(test_url)
    import json
    print(json.dumps(results, indent=2))
