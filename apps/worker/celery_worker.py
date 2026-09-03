import os
import sys
import logging
from celery import Celery
from dotenv import load_dotenv

# Ensure the root project directory is in the python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, base_dir)

# Load environment variables
load_dotenv(os.path.join(base_dir, 'apps', 'api', '.env'))

# Import the DB sessions
from apps.api.db.session import SessionLocal, neo4j_driver
from sqlalchemy import text

# Import the collectors and ml engines
from services.collection_engine.collectors.shodan_collector import ShodanCollector
from services.collection_engine.collectors.virustotal_collector import VirusTotalCollector
from services.collection_engine.collectors.blockcypher_collector import BlockcypherCollector
from services.ml_engine.fusion import EvidenceFusionEngine
from services.ml_engine.adversarial import AdversarialEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("prism_worker", broker=redis_url, backend=redis_url)

@celery_app.task(name="ingest_target")
def ingest_target(target: str, target_type: str, investigation_id: str):
    """
    Ingests a target by running OSINT collection, fusing evidence, and storing the result in DB.
    """
    logger.info(f"Starting ingestion for target: {target} (type: {target_type}) in investigation: {investigation_id}")
    
    evidence_list = []
    
    try:
        # 1. Run Collectors
        if target_type == 'ip':
            collector = ShodanCollector(target)
            evidence_list.extend(collector.run())
        elif target_type == 'domain':
            collector = VirusTotalCollector(target)
            evidence_list.extend(collector.run())
        elif target_type == 'wallet':
            collector = BlockcypherCollector(target)
            evidence_list.extend(collector.run())
            
        logger.info(f"Collected {len(evidence_list)} pieces of evidence from OSINT.")
        
        # 2. Store to PostgreSQL (Mocked insertion - schema assumes an observations or evidence table)
        # Using a raw query for simplicity until full SQLAlchemy models are available
        db = SessionLocal()
        try:
            # Check if investigations table exists and insert if needed
            db.execute(text("""
                INSERT INTO investigations (id, name, status) 
                VALUES (:id, :name, 'active')
                ON CONFLICT (id) DO NOTHING
            """), {"id": investigation_id, "name": f"Investigation for {target}"})
            
            # Insert Evidence
            for ev in evidence_list:
                db.execute(text("""
                    INSERT INTO evidence (investigation_id, category, source_id, data) 
                    VALUES (:inv_id, :cat, :src, :data)
                """), {
                    "inv_id": investigation_id, 
                    "cat": ev["type"], 
                    "src": target_type, 
                    "data": str(ev)
                })
            db.commit()
            logger.info("Saved evidence to PostgreSQL")
        except Exception as e:
            db.rollback()
            logger.error(f"PostgreSQL Error: {e}")
        finally:
            db.close()
            
        # 3. ML Fusion & Adversarial checking
        fusion_engine = EvidenceFusionEngine()
        for ev in evidence_list:
            # Map OSINT evidence to ML Engine groups
            group = "Network" if target_type == 'ip' else "Infrastructure" if target_type == 'domain' else "Blockchain"
            fusion_engine.add_evidence(
                name=f"{ev['type']}: {ev['value']}", 
                score=ev['confidence'], 
                group=group, 
                reliability=0.9
            )
            
        confidence, group_scores = fusion_engine.calculate_hybrid_bayesian_probability(prior=0.1)
        
        adv_engine = AdversarialEngine(fusion_engine)
        adv_results = adv_engine.run_leave_one_out_analysis(prior=0.1)
        robustness = adv_engine.evaluate_robustness(adv_results)
        
        # 4. Save Graph data to Neo4j
        try:
            with neo4j_driver.session() as session:
                # Merge the investigation/cluster node
                session.run("""
                    MERGE (c:ActorCluster {id: $id})
                    SET c.title = $title,
                        c.confidence = $confidence,
                        c.robustness = $robustness
                """, id=investigation_id, title=f"Target: {target}", confidence=confidence, robustness=robustness)
                
                # Link Evidence nodes
                for ev in evidence_list:
                    session.run("""
                        MATCH (c:ActorCluster {id: $id})
                        MERGE (e:Evidence {value: $value})
                        SET e.type = $type, e.confidence = $ev_conf
                        MERGE (c)-[:SUPPORTED_BY]->(e)
                    """, id=investigation_id, value=ev['value'], type=ev['type'], ev_conf=ev['confidence'])
            
            logger.info("Saved graph data to Neo4j")
        except Exception as e:
            logger.error(f"Neo4j Error: {e}")
            
        return {"status": "success", "evidence_count": len(evidence_list)}
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return {"status": "failed", "error": str(e)}
