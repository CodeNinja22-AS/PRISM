import os
from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)

class GraphEngine:
    """
    Phase 11: Threat Actor Knowledge Graph Connection
    Manages connections and transactions to the Neo4j database.
    """
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("Successfully connected to Neo4j graph database.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def create_actor_cluster(self, cluster_id, confidence, robustness):
        """Creates a central Threat Actor Cluster node."""
        query = (
            "MERGE (a:ActorCluster { id: $cluster_id }) "
            "SET a.confidence = $confidence, a.robustness = $robustness, a.last_updated = timestamp() "
            "RETURN a"
        )
        with self.driver.session() as session:
            result = session.run(query, cluster_id=cluster_id, confidence=confidence, robustness=robustness)
            return result.single()

    def add_persona(self, persona_id, aliases, actor_cluster_id=None):
        """Creates a Persona node and optionally links it to an ActorCluster."""
        query = (
            "MERGE (p:Persona { id: $persona_id }) "
            "SET p.aliases = $aliases, p.last_updated = timestamp() "
        )
        params = {"persona_id": persona_id, "aliases": aliases}
        
        if actor_cluster_id:
            query += "WITH p MATCH (a:ActorCluster { id: $actor_cluster_id }) "
            query += "MERGE (p)-[:BELONGS_TO]->(a) "
            params["actor_cluster_id"] = actor_cluster_id
            
        query += "RETURN p"
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            return result.single()

    def add_infrastructure(self, domain, ip_address, persona_id=None):
        """Adds a server/domain and optionally connects to a Persona."""
        query = (
            "MERGE (s:Server { ip: $ip_address }) "
            "MERGE (d:Domain { name: $domain }) "
            "MERGE (d)-[:HOSTED_ON]->(s) "
        )
        params = {"domain": domain, "ip_address": ip_address}
        
        if persona_id:
            query += "WITH d MATCH (p:Persona { id: $persona_id }) "
            query += "MERGE (p)-[:CONTROLS]->(d) "
            params["persona_id"] = persona_id
            
        query += "RETURN s, d"
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            return result.single()

    def link_wallets(self, wallet_a, wallet_b, transaction_hash):
        """Links two wallets via a transaction."""
        query = (
            "MERGE (wa:Wallet { address: $wallet_a }) "
            "MERGE (wb:Wallet { address: $wallet_b }) "
            "MERGE (wa)-[:TRANSACTED_WITH { tx: $tx_hash, timestamp: timestamp() }]->(wb) "
            "RETURN wa, wb"
        )
        with self.driver.session() as session:
            result = session.run(query, wallet_a=wallet_a, wallet_b=wallet_b, tx_hash=transaction_hash)
            return result.single()
