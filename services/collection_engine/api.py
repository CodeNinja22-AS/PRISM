from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Import the analytical engines
from analysis.fusion import EvidenceFusionEngine
from analysis.adversarial import AdversarialEngine
from analysis.persona import PersonaProfile, PersonaIntelligenceEngine
from analysis.infrastructure import InfrastructureGraph

app = FastAPI(title="PRISM Intelligence API")

# Configure CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def get_status():
    return {"status": "online", "engines": ["fusion", "adversarial", "persona", "infrastructure"]}

@app.get("/api/investigation/{inv_id}")
def get_investigation_details(inv_id: str):
    """
    Simulates retrieving a full investigation object by running the fusion 
    and adversarial engines on mock data.
    """
    # 1. Setup Mock Fusion Engine (from Phase 12)
    fusion_engine = EvidenceFusionEngine()
    fusion_engine.add_evidence("Traffic Timing Correlation", 0.92, group="Network", reliability=0.95)
    fusion_engine.add_evidence("Wallet Co-spending", 0.87, group="Blockchain", reliability=0.99)
    fusion_engine.add_evidence("Shared Clearnet IP", 0.81, group="Infrastructure", reliability=0.90)
    fusion_engine.add_evidence("Active Hours Overlap", 0.78, group="Behavior", reliability=0.85)
    fusion_engine.add_evidence("Linguistic Profile", 0.74, group="Stylometry", reliability=0.60)
    
    # 2. Run Fusion
    confidence, group_scores = fusion_engine.calculate_hybrid_bayesian_probability(prior=0.1)
    
    # 3. Run Adversarial
    adv_engine = AdversarialEngine(fusion_engine)
    adv_results = adv_engine.run_leave_one_out_analysis(prior=0.1)
    robustness = adv_engine.evaluate_robustness(adv_results)
    
    return {
        "id": inv_id,
        "title": "Threat Actor Alpha",
        "metrics": {
            "confidence": confidence,
            "robustness": robustness,
            "evidence_count": len(fusion_engine.evidence_pool),
            "contradictions": 0, # Mocked
            "entities": 15 # Mocked
        },
        "adversarial_report": {
            "questions": adv_results["adversarial_questions"],
            "most_critical_evidence": adv_results["most_critical"],
            "leave_one_out": adv_results["leave_one_out"]
        },
        "evidence_breakdown": [
            {"name": ev.name, "score": ev.score, "group": ev.independence_group}
            for ev in fusion_engine.evidence_pool
        ]
    }

@app.get("/api/graph/{inv_id}")
def get_actor_graph(inv_id: str):
    """
    Returns nodes and edges for the React Flow frontend.
    Simulating the Neo4j/Infrastructure graph structure.
    """
    nodes = [
        {"id": "Actor_A", "data": {"label": "Threat Actor Alpha", "type": "ActorCluster"}},
        {"id": "Persona_A", "data": {"label": "Admin_Omega", "type": "Persona"}},
        {"id": "PGP_1", "data": {"label": "0xABCD1234", "type": "PGPKey"}},
        {"id": "Wallet_1", "data": {"label": "bc1qxy2kg...", "type": "Wallet"}},
        {"id": "Domain_1", "data": {"label": "omega-market.onion", "type": "Infrastructure"}},
        {"id": "IP_1", "data": {"label": "198.51.100.42 (Leaked)", "type": "Infrastructure", "alert": True}},
        {"id": "Trace_1", "data": {"label": "Traffic Trace #001", "type": "Traffic"}},
    ]
    
    edges = [
        {"id": "e1", "source": "Actor_A", "target": "Persona_A", "label": "CONTROLS"},
        {"id": "e2", "source": "Persona_A", "target": "PGP_1", "label": "USES"},
        {"id": "e3", "source": "Persona_A", "target": "Domain_1", "label": "ADMINISTERS"},
        {"id": "e4", "source": "Domain_1", "target": "IP_1", "label": "HOSTED_ON"},
        {"id": "e5", "source": "Actor_A", "target": "Wallet_1", "label": "OWNS"},
        {"id": "e6", "source": "Persona_A", "target": "Trace_1", "label": "CORRELATED"},
    ]
    
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting PRISM API wrapper on http://0.0.0.0:8000")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
