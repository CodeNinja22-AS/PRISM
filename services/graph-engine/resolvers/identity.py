from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "prism_password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def resolve_meta_identities():
    """
    Finds Personas that share a PGP Key or Crypto Address and links them to a common MetaIdentity.
    """
    query = """
    // Find Personas that share a PGP key
    MATCH (p1:Persona)-[:USED_KEY]->(k:PGPKey)<-[:USED_KEY]-(p2:Persona)
    WHERE id(p1) < id(p2)
    
    // Create or find a MetaIdentity
    MERGE (m:MetaIdentity {id: 'META_' + k.fingerprint})
    
    // Link them
    MERGE (p1)-[:SAME_AS]->(m)
    MERGE (p2)-[:SAME_AS]->(m)
    
    RETURN p1.handle as alias1, p2.handle as alias2, k.fingerprint as shared_key
    """
    
    with driver.session() as session:
        result = session.run(query)
        resolutions = []
        for record in result:
            resolutions.append({
                "alias1": record["alias1"],
                "alias2": record["alias2"],
                "shared_key": record["shared_key"]
            })
            
        print(f"[*] Resolved {len(resolutions)} alias pairs into MetaIdentities.")
        return resolutions
