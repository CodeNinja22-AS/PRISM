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

@router.get("/topology/{id}")
def get_topology(id: str, session: Neo4jSession = Depends(get_neo4j)):
    """
    Fetches the actual React Flow topology from Neo4j based on investigation or cluster id.
    """
    query = """
    MATCH (n)-[r]-(m)
    WHERE n.investigation_id = $id OR n.cluster_id = $id OR n.id = $id
    RETURN n, r, m
    LIMIT 300
    """
    result = session.run(query, id=id)
    
    nodes_dict = {}
    edges_dict = {}
    
    for record in result:
        n = record["n"]
        if n.element_id not in nodes_dict:
            label = list(n.labels)[0] if n.labels else "Unknown"
            name = n.get("name") or n.get("handle") or n.get("url") or n.get("value") or label
            nodes_dict[n.element_id] = {
                "id": str(n.element_id),
                "data": {"label": name, "type": label},
                "position": {"x": 0, "y": 0} # Frontend layout engine (like Dagre) should set positions
            }
            
        m = record["m"]
        if m.element_id not in nodes_dict:
            label = list(m.labels)[0] if m.labels else "Unknown"
            name = m.get("name") or m.get("handle") or m.get("url") or m.get("value") or label
            nodes_dict[m.element_id] = {
                "id": str(m.element_id),
                "data": {"label": name, "type": label},
                "position": {"x": 0, "y": 0}
            }
            
        r = record["r"]
        edge_id = str(r.element_id)
        if edge_id not in edges_dict:
            edges_dict[edge_id] = {
                "id": edge_id,
                "source": str(r.start_node.element_id),
                "target": str(r.end_node.element_id),
                "label": r.type,
                "animated": True
            }
        
    return {
        "nodes": list(nodes_dict.values()),
        "edges": list(edges_dict.values())
    }
