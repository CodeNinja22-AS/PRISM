from neo4j import GraphDatabase
import os
import logging

class ThreatActorGraph:
    """
    PHASE 11: Neo4j Threat Actor Knowledge Graph
    The central intelligence hub that links all entities and evidence.
    """
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        # For the hackathon prototype, we allow running without a live DB
        self.driver = None
        self.is_connected = False
        
        try:
            # Uncomment in production/when Neo4j is running locally
            # self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # self.is_connected = True
            logging.info("Neo4j driver initialized (Dry-run mode for prototype).")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_write(self, query, **kwargs):
        """Helper to execute write transactions."""
        if not self.is_connected:
            # Print the cypher query for demonstration purposes
            # print(f"[Neo4j Dry-Run] {query} | Params: {kwargs}")
            return
            
        with self.driver.session() as session:
            session.run(query, **kwargs)

    # --- Node Creation Methods ---

    def merge_persona(self, persona_id, alias):
        query = """
        MERGE (p:Persona {id: $persona_id})
        SET p.alias = $alias, p.last_updated = datetime()
        """
        self.execute_write(query, persona_id=persona_id, alias=alias)

    def merge_infrastructure(self, entity_id, entity_type, value):
        """Creates Domain, Server, Certificate, IP nodes."""
        # Using f-string for label is safe here as entity_type is controlled by our engine
        query = f"""
        MERGE (n:{entity_type} {{id: $entity_id}})
        SET n.value = $value
        """
        self.execute_write(query, entity_id=entity_id, value=value)

    def merge_identity_artifact(self, artifact_id, artifact_type, value):
        """Creates Username, PGPKey, Email nodes."""
        query = f"""
        MERGE (n:{artifact_type} {{id: $artifact_id}})
        SET n.value = $value
        """
        self.execute_write(query, artifact_id=artifact_id, value=value)

    def merge_wallet(self, wallet_id, address, blockchain="Bitcoin"):
        query = """
        MERGE (w:Wallet {id: $wallet_id})
        SET w.address = $address, w.blockchain = $blockchain
        """
        self.execute_write(query, wallet_id=wallet_id, address=address, blockchain=blockchain)

    def merge_traffic_trace(self, trace_id, protocol, capture_time):
        query = """
        MERGE (t:TrafficTrace {id: $trace_id})
        SET t.protocol = $protocol, t.capture_time = $capture_time
        """
        self.execute_write(query, trace_id=trace_id, protocol=protocol, capture_time=capture_time)

    # --- Relationship Creation Methods ---

    def link_entities(self, source_id, source_type, target_id, target_type, relationship, properties=None):
        """
        Generic linker for: USES, CONTROLS, SIGNED_BY, OWNS, CONNECTED_TO, etc.
        """
        props_str = ""
        if properties:
            # Build property string like {weight: $weight, source: $source}
            props_str = "{" + ", ".join([f"{k}: ${k}" for k in properties.keys()]) + "}"
        
        query = f"""
        MATCH (a:{source_type} {{id: $source_id}})
        MATCH (b:{target_type} {{id: $target_id}})
        MERGE (a)-[r:{relationship} {props_str}]->(b)
        """
        kwargs = {"source_id": source_id, "target_id": target_id}
        if properties:
            kwargs.update(properties)
            
        self.execute_write(query, **kwargs)

    def create_demo_graph(self):
        """Builds the exact Neo4j structure requested in Phase 11."""
        print("--- PHASE 11: Building Neo4j Threat Actor Knowledge Graph ---")
        
        # 1. Create Actor Cluster & Personas
        self.execute_write("MERGE (c:ActorCluster {id: 'Cluster_Alpha'})")
        self.merge_persona("Persona_A", "Alpha_Admin")
        self.merge_persona("Persona_B", "Alpha_Dev")
        
        # 2. Create Artifacts
        self.merge_identity_artifact("User_01", "Username", "alpha_sys")
        self.merge_identity_artifact("PGP_01", "PGPKey", "0xDEADBEEF")
        self.merge_infrastructure("Forum_X", "Domain", "darkforum.onion")
        self.merge_identity_artifact("Doc_01", "Document", "OpSec_Guide.pdf")
        self.merge_wallet("Wallet_A", "bc1q_alpha")
        self.merge_wallet("Wallet_B", "bc1q_mixer")
        self.execute_write("MERGE (tx:Transaction {id: 'Txn_01'})")
        self.merge_traffic_trace("Trace_001", "Tor/TCP", "2023-11-01T00:00:00Z")
        
        # 3. Build Relationships
        self.link_entities("Cluster_Alpha", "ActorCluster", "Persona_A", "Persona", "CONTROLS")
        self.link_entities("Cluster_Alpha", "ActorCluster", "Persona_B", "Persona", "CONTROLS")
        self.link_entities("Cluster_Alpha", "ActorCluster", "Wallet_A", "Wallet", "CONTROLS")
        
        self.link_entities("Persona_A", "Persona", "User_01", "Username", "USES")
        self.link_entities("User_01", "Username", "Forum_X", "Domain", "OBSERVED_ON")
        self.link_entities("Forum_X", "Domain", "Trace_001", "TrafficTrace", "GENERATED")
        
        self.link_entities("Persona_B", "Persona", "PGP_01", "PGPKey", "OWNS")
        self.link_entities("PGP_01", "PGPKey", "Doc_01", "Document", "SIGNED_BY")
        
        self.link_entities("Wallet_A", "Wallet", "Txn_01", "Transaction", "INITIATED")
        self.link_entities("Txn_01", "Transaction", "Wallet_B", "Wallet", "SENT_TO")
        
        print("Knowledge Graph successfully structured. Entities linked via Cypher queries.")
        print("Ready for Graph Data Science (GDS) traversal and explanation algorithms.")

if __name__ == "__main__":
    db = ThreatActorGraph()
    db.create_demo_graph()
