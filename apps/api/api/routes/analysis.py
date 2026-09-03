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
from neo4j import Session as Neo4jSession
from db.session import get_neo4j
from fastapi import APIRouter, Depends, HTTPException
router = APIRouter()
graph_engine = GraphEngine()

import uuid
from pydantic import BaseModel

# Try to import celery worker task, fail gracefully if not accessible in this context
try:
    from apps.worker.celery_worker import ingest_target
except ImportError:
    ingest_target = None

class AnalysisRequest(BaseModel):
    cluster_id: str

class IngestRequest(BaseModel):
    target: str
    target_type: str # 'ip', 'domain', 'wallet'
    
@router.post("/ingest")
def trigger_ingestion(request: IngestRequest):
    """
    Trigger the Celery background worker to ingest a target.
    """
    investigation_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    
    if ingest_target:
        # Submit to Celery
        task = ingest_target.delay(request.target, request.target_type, investigation_id)
        return {
            "status": "Processing",
            "task_id": task.id,
            "investigation_id": investigation_id
        }
    else:
        raise HTTPException(status_code=500, detail="Celery worker not configured")

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
    try:
        graph_engine.create_actor_cluster(
            cluster_id=request.cluster_id,
            confidence=results['baseline'],
            robustness=robustness
        )
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
    
    return {
        "cluster_id": request.cluster_id,
        "confidence": results["baseline"],
        "robustness": robustness,
        "critical_evidence_group": results["most_critical"],
        "adversarial_questions": results["adversarial_questions"]
    }

@router.get("/investigation/{id}")
def get_investigation(id: str, session: Neo4jSession = Depends(get_neo4j)):
    """
    Fetches investigation details and metrics from Neo4j ActorCluster nodes.
    """
    # Query for the ActorCluster and its connected Evidence
    query = """
    MATCH (c:ActorCluster {id: $id})
    OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(e:Evidence)
    RETURN c, collect(e) as evidence_list
    """
    
    result = session.run(query, id=id).data()
    
    if not result or not result[0].get("c"):
        # Fallback if not found in db, maybe it's just being processed
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    cluster_node = result[0]["c"]
    evidence_nodes = result[0]["evidence_list"]
    
    # Process evidence
    evidence_breakdown = []
    for ev in evidence_nodes:
        if ev:
            evidence_breakdown.append({
                "name": ev.get("name", "Unknown Evidence"),
                "group": ev.get("group", "General"),
                "score": ev.get("score", 0.0)
            })
            
    # Default structure
    return {
        "title": cluster_node.get("title", f"Investigation {id}"),
        "id": id,
        "metrics": {
            "confidence": cluster_node.get("confidence", 0.0),
            "robustness": cluster_node.get("robustness", 0.0)
        },
        "evidence_breakdown": evidence_breakdown,
        "adversarial_report": {
            "questions": cluster_node.get("adversarial_questions", []),
            "leave_one_out": cluster_node.get("leave_one_out_scores", {})
        }
    }
