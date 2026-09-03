from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

from collectors.shodan_collector import ShodanCollector
from collectors.virustotal_collector import VirusTotalCollector
from collectors.blockcypher_collector import BlockcypherCollector

app = FastAPI(title="PRISM OSINT Collection API")

class CollectionRequest(BaseModel):
    target: str
    target_type: str # 'ip', 'domain', 'wallet'

@app.post("/api/collect")
def run_collection(request: CollectionRequest):
    evidence = []
    
    try:
        if request.target_type == 'ip':
            collector = ShodanCollector(request.target)
            evidence.extend(collector.run())
        elif request.target_type == 'domain':
            collector = VirusTotalCollector(request.target)
            evidence.extend(collector.run())
        elif request.target_type == 'wallet':
            collector = BlockcypherCollector(request.target)
            evidence.extend(collector.run())
        else:
            raise HTTPException(status_code=400, detail="Unknown target type")
            
        return {
            "target": request.target,
            "evidence": evidence
        }
    except Exception as e:
        logging.error(f"Collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting PRISM OSINT Collection API on http://0.0.0.0:8001")
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
