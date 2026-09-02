class ClearnetMatcher:
    def correlate(self, http_data: dict, tls_data: dict) -> dict:
        """
        Correlates extracted dark web indicators to hypothesize a clearnet origin.
        """
        candidate_origins = []
        confidence = 0.0
        
        # TLS match is a very strong indicator of misconfiguration
        if tls_data and tls_data.get("sans"):
            candidate_origins.extend(tls_data["sans"])
            confidence += 0.8
            
        # Banner / Server-status match (mock Shodan lookup)
        if http_data and http_data.get("exposed_server_status"):
            # In a real scenario, we'd query Shodan for this specific banner + title
            candidate_origins.append("198.51.100.42 (Mock IP)")
            confidence += 0.15
            
        return {
            "candidate_origins": list(set(candidate_origins)),
            "confidence_score": min(confidence, 1.0)
        }
