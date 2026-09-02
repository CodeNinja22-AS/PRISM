from datetime import datetime

def normalize_forum_post(raw_post, source_id, reliability):
    """
    Normalizes a raw forum post into the Evidence schema format.
    """
    evidence_id = f"{source_id}_{raw_post['id']}"
    
    # Handle timestamp format robustly
    ts = raw_post.get("timestamp")
    
    normalized = {
        "id": evidence_id,
        "category": "Identity",
        "source_id": source_id,
        "first_seen": ts,
        "last_seen": ts,
        "last_scan": datetime.utcnow().isoformat(),
        "reliability": reliability,
        "data": {
            "author": raw_post.get("author"),
            "content": raw_post.get("content"),
            "pgp_key_fingerprint": raw_post.get("pgp_key_fingerprint"),
            "metadata": raw_post.get("metadata", {})
        }
    }
    return normalized
