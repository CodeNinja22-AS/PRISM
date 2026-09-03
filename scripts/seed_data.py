import os
import sys
from neo4j import GraphDatabase

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from apps.api.core.config import settings

def seed():
    uri = settings.NEO4J_URI
    user = settings.NEO4J_USER
    password = settings.NEO4J_PASSWORD
    
    print(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Clear existing
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing graph data.")
        
        # Create Investigation
        session.run("""
        CREATE (i:Investigation {id: 'INV-TA017', title: 'Operation Silk Route'})
        """)
        
        # Create Actor Clusters
        session.run("""
        CREATE (c1:ActorCluster {id: 'TA-017', title: 'Alpha Syndicate', confidence: 0.94, robustness: 0.88, investigation_id: 'INV-TA017'})
        CREATE (c2:ActorCluster {id: 'TA-018', title: 'Bravo Nexus', confidence: 0.65, robustness: 0.42, investigation_id: 'INV-TA017'})
        CREATE (c3:ActorCluster {id: 'TA-019', title: 'Charlie Group', confidence: 0.82, robustness: 0.76, investigation_id: 'INV-TA017'})
        """)
        
        # Create Evidence nodes
        session.run("""
        MATCH (c:ActorCluster {id: 'TA-017'})
        CREATE (e1:Evidence {name: 'Traffic Timing (Ensemble)', group: 'Network', score: 0.92})
        CREATE (e2:Evidence {name: 'Wallet Co-spending', group: 'Blockchain', score: 0.87})
        CREATE (e3:Evidence {name: 'Linguistic Profile', group: 'Stylometry', score: 0.74})
        CREATE (c)-[:SUPPORTED_BY]->(e1)
        CREATE (c)-[:SUPPORTED_BY]->(e2)
        CREATE (c)-[:SUPPORTED_BY]->(e3)
        """)
        
        # Create topology for TA-017
        session.run("""
        CREATE (ta:ThreatActor {element_id: 'node-ta017', name: 'Target Alpha', cluster_id: 'TA-017'})
        CREATE (sb:ThreatActor {element_id: 'node-sb', name: 'Suspect Bravo', cluster_id: 'TA-017'})
        CREATE (btc:CryptoWallet {element_id: 'node-btc', name: 'BTC: 1A1zP...', cluster_id: 'TA-017'})
        CREATE (ip:Infrastructure {element_id: 'node-ip', name: 'IP: 198.51.100.14', cluster_id: 'TA-017'})
        CREATE (meta:Metadata {element_id: 'node-meta', name: 'Metadata: EXIF iPhone 13', cluster_id: 'TA-017'})
        
        CREATE (ta)-[:OPERATES {element_id: 'edge-1', type: 'OPERATES'}]->(btc)
        CREATE (sb)-[:OPERATES {element_id: 'edge-2', type: 'OPERATES'}]->(ip)
        CREATE (ta)-[:CONNECTED_TO {element_id: 'edge-3', type: 'CONNECTED_TO'}]->(ip)
        CREATE (sb)-[:SHARED_METADATA {element_id: 'edge-4', type: 'SHARED_METADATA'}]->(meta)
        CREATE (ta)-[:SHARED_METADATA {element_id: 'edge-5', type: 'SHARED_METADATA'}]->(meta)
        """)
        
        # Create topology for TA-018
        session.run("""
        CREATE (ta2:ThreatActor {element_id: 'node-ta018', name: 'Target Gamma', cluster_id: 'TA-018'})
        CREATE (ip2:Infrastructure {element_id: 'node-ip2', name: 'IP: 203.0.113.45', cluster_id: 'TA-018'})
        CREATE (ta2)-[:OPERATES {element_id: 'edge-6', type: 'OPERATES'}]->(ip2)
        """)
        
        print("Seeded Neo4j successfully with mock clusters, evidence, and topology!")
        
    driver.close()

if __name__ == "__main__":
    seed()
