from fastapi import APIRouter, HTTPException
import sys
import os

# Ensure the services directory is accessible
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, base_dir)

from pydantic import BaseModel
from services.ml_engine.fusion import EvidenceFusionEngine
from services.ml_engine.adversarial import AdversarialEngine
from services.graph_engine.neo4j_driver import GraphEngine

router = APIRouter()
graph_engine = GraphEngine()

class AnalysisRequest(BaseModel):
    cluster_id: str

@router.post("/cluster")
def analyze_cluster(request: AnalysisRequest):
    """
    Run adversarial and fusion analysis on an Actor Cluster.
    """
    fusion_engine = EvidenceFusionEngine()
    
    # In production, fetch these from DB based on cluster_id
    fusion_engine.add_evidence("Traffic Timing", 0.92, group="Network", reliability=0.95)
    fusion_engine.add_evidence("Wallet Co-spending", 0.87, group="Blockchain", reliability=0.99)
    fusion_engine.add_evidence("Shared Clearnet IP", 0.81, group="Infrastructure", reliability=0.90)
    fusion_engine.add_evidence("Active Hours Overlap", 0.78, group="Behavior", reliability=0.85)
    
    adv_engine = AdversarialEngine(fusion_engine)
    results = adv_engine.run_leave_one_out_analysis(prior=0.1)
    robustness = adv_engine.evaluate_robustness(results)
    
    # Update Neo4j graph with calculated intelligence metrics
    graph_engine.create_actor_cluster(
        cluster_id=request.cluster_id,
        confidence=results['baseline'],
        robustness=robustness
    )
    
    return {
        "cluster_id": request.cluster_id,
        "confidence": results["baseline"],
        "robustness": robustness,
        "critical_evidence_group": results["most_critical"],
        "adversarial_questions": results["adversarial_questions"]
    }

@router.get("/investigation/{id}")
def get_investigation(id: str):
    """
    Mock endpoint for the PRISM Dashboard to display investigation details.
    In production, this fetches from the Neo4j ActorCluster nodes.
    """
    return {
      "title": "AlphaBay Vendor Migration",
      "id": id,
      "metrics": {
        "confidence": 0.94,
        "robustness": 0.82
      },
      "evidence_breakdown": [
        {"name": "Traffic Timing Correlation", "group": "Network", "score": 0.92},
        {"name": "Wallet Co-spending", "group": "Blockchain", "score": 0.87},
        {"name": "Shared Clearnet IP", "group": "Infrastructure", "score": 0.81},
        {"name": "Active Hours Overlap", "group": "Behavior", "score": 0.78},
        {"name": "Linguistic Profile", "group": "Stylometry", "score": 0.74}
      ],
      "adversarial_report": {
        "questions": [
          "Could traffic similarity be natural coincidence (e.g. streaming same video)?",
          "Could the wallet relationship be indirect (e.g. common darknet market deposit wallet)?"
        ],
        "leave_one_out": {
          "Network": 0.65,
          "Blockchain": 0.72,
          "Infrastructure": 0.89,
          "Behavior": 0.91,
          "Stylometry": 0.93
        }
      }
    }
