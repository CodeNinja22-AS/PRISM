import os
import shodan
from typing import List, Dict, Any
from .base import BaseCollector

class ShodanCollector(BaseCollector):
    def __init__(self, target_ip: str):
        super().__init__(source_id="shodan")
        self.target_ip = target_ip
        self.api_key = os.getenv("SHODAN_API_KEY", "")
        self.reliability = 0.95
        if not self.api_key:
            raise ValueError("SHODAN_API_KEY is not set in environment.")
        self.api = shodan.Shodan(self.api_key)

    def fetch_data(self) -> Any:
        try:
            return self.api.host(self.target_ip)
        except shodan.APIError as e:
            print(f"Shodan API Error: {e}")
            return None

    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        if not raw_data:
            return []
        
        evidence = []
        
        # Extract open ports
        ports = raw_data.get('ports', [])
        for port in ports:
            evidence.append({
                "type": "OpenPort",
                "value": port,
                "confidence": 1.0
            })
            
        # Extract vulnerabilities if available
        vulns = raw_data.get('vulns', [])
        for vuln in vulns:
            evidence.append({
                "type": "Vulnerability",
                "value": vuln,
                "confidence": 0.9
            })
            
        # Extract hostnames
        hostnames = raw_data.get('hostnames', [])
        for hostname in hostnames:
            evidence.append({
                "type": "Domain",
                "value": hostname,
                "confidence": 0.95
            })

        return evidence
