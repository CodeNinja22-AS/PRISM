from fastapi import APIRouter, Depends, HTTPException
from neo4j import Session as Neo4jSession
from db.session import get_neo4j

router = APIRouter()

@router.get("/all")
def get_all_clusters(session: Neo4jSession = Depends(get_neo4j)):
    """
    Retrieves all macro-level threat actor clusters from Neo4j.
    """
    query = """
    MATCH (c:ActorCluster)
    OPTIONAL MATCH (c)-[:CONTAINS]->(n)
    RETURN c.id AS id, c.title AS title, c.confidence AS confidence, 
           c.robustness AS robustness, count(n) AS node_count
    ORDER BY c.confidence DESC
    """
    try:
        result = session.run(query).data()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

    clusters = []
    for record in result:
        clusters.append({
            "id": record["id"],
            "title": record["title"],
            "confidence": record["confidence"] or 0.0,
            "robustness": record["robustness"] or 0.0,
            "node_count": record["node_count"] or 0
        })
        
    return {"clusters": clusters}
