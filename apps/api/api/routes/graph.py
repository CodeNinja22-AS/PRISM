from fastapi import APIRouter, Depends, HTTPException
from neo4j import Session as Neo4jSession
from db.session import get_neo4j
from typing import List, Dict, Any

router = APIRouter()

@router.get("/persona/{handle}")
def get_persona_footprint(handle: str, session: Neo4jSession = Depends(get_neo4j)):
    """
    Executes the find_persona_footprint Cypher query to get a persona's subgraph.
    """
    query = """
    MATCH (p:Persona {handle: $handle})-[r]-(n)
    RETURN type(r) AS relationship, labels(n) AS node_type, n AS properties
    """
    result = session.run(query, handle=handle)
    return [dict(record) for record in result]

@router.get("/infrastructure-overlap")
def get_infrastructure_overlap(session: Neo4jSession = Depends(get_neo4j)):
    """
    Identifies hidden services sharing clearnet assets.
    """
    query = """
    MATCH (h1:HiddenService)-[:HAS_ASSET]->(a:ClearnetAsset)<-[:HAS_ASSET]-(h2:HiddenService)
    WHERE id(h1) < id(h2)
    RETURN h1.url AS service1, h2.url AS service2, a.value AS shared_asset
    """
    result = session.run(query)
    return [dict(record) for record in result]
