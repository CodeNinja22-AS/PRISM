import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "prism_password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def apply_constraints():
    queries = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Persona) REQUIRE p.handle IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Evidence) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (k:PGPKey) REQUIRE k.fingerprint IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:CryptoAddress) REQUIRE c.address IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (m:MetaIdentity) REQUIRE m.id IS UNIQUE"
    ]
    
    with driver.session() as session:
        for q in queries:
            try:
                session.run(q)
                print(f"[+] Applied constraint: {q.split('FOR')[1].strip()}")
            except Exception as e:
                print(f"[!] Failed to apply constraint: {e}")

if __name__ == "__main__":
    apply_constraints()
