import os
import vt
from typing import List, Dict, Any
from .base import BaseCollector

class VirusTotalCollector(BaseCollector):
    def __init__(self, target_domain: str):
        super().__init__(source_id="virustotal")
        self.target_domain = target_domain
        self.api_key = os.getenv("VT_API_KEY", "")
        self.reliability = 0.90
        if not self.api_key:
            raise ValueError("VT_API_KEY is not set in environment.")
        
    def fetch_data(self) -> Any:
        try:
            with vt.Client(self.api_key) as client:
                # Get information about a domain
                domain_id = self.target_domain
                return client.get_object(f"/domains/{domain_id}")
        except vt.APIError as e:
            print(f"VirusTotal API Error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching from VirusTotal: {e}")
            return None

    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        if not raw_data:
            return []
        
        evidence = []
        
        # Extract reputation score
        reputation = getattr(raw_data, 'reputation', 0)
        evidence.append({
            "type": "ReputationScore",
            "value": reputation,
            "confidence": 0.95
        })
        
        # Extract last DNS records
        dns_records = getattr(raw_data, 'last_dns_records', [])
        for record in dns_records:
            if record.get('type') == 'A':
                evidence.append({
                    "type": "IPAddress",
                    "value": record.get('value'),
                    "confidence": 0.90
                })
                
        # Malicious stats
        analysis_stats = getattr(raw_data, 'last_analysis_stats', {})
        malicious = analysis_stats.get('malicious', 0)
        if malicious > 0:
            evidence.append({
                "type": "MaliciousFlag",
                "value": True,
                "confidence": min(1.0, malicious * 0.1)
            })

        return evidence
