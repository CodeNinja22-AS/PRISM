from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "prism_password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def find_infrastructure_overlap():
    """
    Finds hidden services sharing the same clearnet assets (e.g. TLS certificates).
    """
    query = """
    MATCH (h1:HiddenService)-[:HAS_ASSET]->(a:ClearnetAsset)<-[:HAS_ASSET]-(h2:HiddenService)
    WHERE id(h1) < id(h2)
    RETURN h1.url AS service1, h2.url AS service2, a.value AS shared_asset
    """
    
    with driver.session() as session:
        return [dict(record) for record in session.run(query)]

def find_persona_footprint(handle: str):
    """
    Returns the full subgraph properties for a given handle.
    """
    query = """
    MATCH (p:Persona {handle: $handle})-[r]-(n)
    RETURN type(r) AS relationship, labels(n) AS node_type, n AS properties
    """
    
    with driver.session() as session:
        return [dict(record) for record in session.run(query, handle=handle)]
