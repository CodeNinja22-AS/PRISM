import datetime

def format_infrastructure_evidence(target_url: str, correlation_result: dict) -> dict:
    """
    Wraps the correlation hypothesis into the standard Evidence envelope.
    """
    # Create a unique ID
    safe_url = target_url.replace("http://", "").replace("https://", "").replace("/", "_")
    evidence_id = f"INFRA_{safe_url}_{int(datetime.datetime.utcnow().timestamp())}"
    
    return {
        "id": evidence_id,
        "category": "Infrastructure",
        "source_id": "hidden-service-engine",
        "first_seen": datetime.datetime.utcnow().isoformat(),
        "last_seen": datetime.datetime.utcnow().isoformat(),
        "last_scan": datetime.datetime.utcnow().isoformat(),
        "reliability": correlation_result.get("confidence_score", 0.5),
        "data": {
            "target": target_url,
            "candidate_origins": correlation_result.get("candidate_origins", [])
        }
    }
