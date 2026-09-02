from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
def get_evidence(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve raw evidence collected by the OSINT and Network engines.
    """
    # Using raw SQL for simplicity since the model is defined in another microservice
    query = text("SELECT id, category, source_id, first_seen, reliability, data FROM evidence LIMIT :limit OFFSET :skip")
    result = db.execute(query, {"limit": limit, "skip": skip})
    
    evidence_list = []
    for row in result:
        evidence_list.append({
            "id": row.id,
            "category": row.category,
            "source_id": row.source_id,
            "first_seen": row.first_seen,
            "reliability": row.reliability,
            "data": row.data
        })
    return evidence_list
