import networkx as nx
import numpy as np
from datetime import datetime
from collections import defaultdict

class BlockchainIntelligenceEngine:
    """
    PHASE 9: Blockchain Intelligence
    Normalizes transaction data, builds wallet graphs, and performs 
    clustering/entity resolution to trace funds.
    """
    
    def __init__(self):
        # Directed graph to represent the flow of funds
        self.wallet_graph = nx.DiGraph()
        
        # Raw transactions for temporal analysis
        self.transactions = []
        
        # Known entities (e.g., 'Binance_Hot_Wallet_1')
        self.known_entities = {}
        
        # Cluster assignments mapping wallet_id -> cluster_id
        self.clusters = {}

    def add_known_entity(self, wallet_id, label):
        """Tags a known wallet (e.g., Exchange, Mixer)."""
        self.known_entities[wallet_id] = label
        if not self.wallet_graph.has_node(wallet_id):
            self.wallet_graph.add_node(wallet_id, label=label)
        else:
            self.wallet_graph.nodes[wallet_id]['label'] = label

    def ingest_transaction(self, tx_hash, sender, receiver, amount, timestamp):
        """
        Normalizes and adds transaction data to the pipeline.
        """
        tx = {
            'hash': tx_hash,
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'timestamp': timestamp
        }
        self.transactions.append(tx)
        
        # Build Wallet Graph (Edges represent flow of funds)
        # Weight can represent volume, count can represent frequency
        if self.wallet_graph.has_edge(sender, receiver):
            self.wallet_graph[sender][receiver]['weight'] += amount
            self.wallet_graph[sender][receiver]['count'] += 1
        else:
            self.wallet_graph.add_edge(sender, receiver, weight=amount, count=1)

    def perform_cluster_analysis(self):
        """
        Uses graph algorithms to find clusters of highly connected wallets.
        Heuristics: Co-spending, shared change addresses, or dense subgraph detection.
        (Simplified using undirected connected components for the prototype)
        """
        undirected_G = self.wallet_graph.to_undirected()
        
        # Identify clusters (connected components)
        components = list(nx.connected_components(undirected_G))
        
        for cluster_id, nodes in enumerate(components):
            for node in nodes:
                self.clusters[node] = f"Cluster_{cluster_id}"
                
        return len(components)

    def extract_wallet_features(self, wallet_id):
        """
        Calculates the requested features for a specific wallet.
        """
        if not self.wallet_graph.has_node(wallet_id):
            return {"error": "Wallet not found in graph."}

        # Filter relevant transactions
        in_txs = [tx for tx in self.transactions if tx['receiver'] == wallet_id]
        out_txs = [tx for tx in self.transactions if tx['sender'] == wallet_id]
        all_txs = in_txs + out_txs
        
        if not all_txs:
             return {}
             
        # 1. Transaction Frequency
        timestamps = sorted([tx['timestamp'] for tx in all_txs])
        if len(timestamps) > 1:
            total_duration_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
            frequency = len(all_txs) / total_duration_hours if total_duration_hours > 0 else len(all_txs)
        else:
            frequency = 0
            
        # 2. Transaction Timing (e.g., standard dev of inter-arrival times)
        inter_arrival = np.diff([t.timestamp() for t in timestamps])
        timing_std = np.std(inter_arrival) if len(inter_arrival) > 0 else 0
        
        # 3. Wallet Reuse (Ratio of incoming vs total to see if it's a pass-through/change address)
        reuse_score = len(in_txs) / len(all_txs) if all_txs else 0
        
        # 4. Incoming/Outgoing Patterns (Volume ratio)
        vol_in = sum(tx['amount'] for tx in in_txs)
        vol_out = sum(tx['amount'] for tx in out_txs)
        in_out_ratio = vol_in / vol_out if vol_out > 0 else float('inf')
        
        # 5. Graph Proximity to Known Entities (e.g., Exchanges)
        proximity_to_exchange = None
        for known_wallet, label in self.known_entities.items():
            if "Exchange" in label:
                try:
                    # Shortest path to exchange (peeling chain length)
                    path_len = nx.shortest_path_length(self.wallet_graph, source=wallet_id, target=known_wallet)
                    if proximity_to_exchange is None or path_len < proximity_to_exchange:
                        proximity_to_exchange = path_len
                except nx.NetworkXNoPath:
                    pass

        # 6. Common Counterparties (Degree centralities)
        in_degree = self.wallet_graph.in_degree(wallet_id)
        out_degree = self.wallet_graph.out_degree(wallet_id)
        
        # 7. Cluster Membership
        cluster = self.clusters.get(wallet_id, "Unclustered")

        return {
            "tx_frequency_per_hour": frequency,
            "timing_variance": timing_std,
            "wallet_reuse_score": reuse_score,
            "in_out_vol_ratio": in_out_ratio,
            "hops_to_exchange": proximity_to_exchange if proximity_to_exchange is not None else "No Path",
            "unique_senders": in_degree,
            "unique_receivers": out_degree,
            "cluster_membership": cluster
        }


if __name__ == "__main__":
    print("--- PHASE 9: Blockchain Intelligence Engine Initialization ---")
    
    engine = BlockchainIntelligenceEngine()
    
    # 1. Setup Known Entities
    engine.add_known_entity("Exchange_Deposit_Wallet_X", "Binance Exchange")
    
    # 2. Ingest Synthetic Data (Simulating a splitting/peeling chain)
    # Wallet A -> B, C, D
    # Wallet D -> Exchange
    
    t0 = datetime.now().timestamp()
    print("Ingesting transaction graph...")
    
    # Wallet A distributes funds
    engine.ingest_transaction("tx1", "Wallet_A", "Wallet_B", 5.0, datetime.fromtimestamp(t0))
    engine.ingest_transaction("tx2", "Wallet_A", "Wallet_C", 2.0, datetime.fromtimestamp(t0 + 3600))
    engine.ingest_transaction("tx3", "Wallet_A", "Wallet_D", 8.0, datetime.fromtimestamp(t0 + 7200))
    
    # Wallet D aggregates and sends to exchange
    engine.ingest_transaction("tx4", "Wallet_D", "Exchange_Deposit_Wallet_X", 7.9, datetime.fromtimestamp(t0 + 10000))
    
    # 3. Perform Analysis
    num_clusters = engine.perform_cluster_analysis()
    print(f"\nGenerated graph with {engine.wallet_graph.number_of_nodes()} nodes and {engine.wallet_graph.number_of_edges()} edges.")
    print(f"Identified {num_clusters} interconnected entity clusters.")
    
    # 4. Extract Features
    print("\n--- Wallet Feature Profiles ---")
    
    print("\nTarget Wallet (Wallet A):")
    features_a = engine.extract_wallet_features("Wallet_A")
    for k, v in features_a.items():
        if isinstance(v, float):
             print(f"  {k}: {v:.2f}")
        else:
             print(f"  {k}: {v}")
             
    print("\nIntermediate Node (Wallet D):")
    features_d = engine.extract_wallet_features("Wallet_D")
    for k, v in features_d.items():
        if isinstance(v, float):
             print(f"  {k}: {v:.2f}")
        else:
             print(f"  {k}: {v}")
