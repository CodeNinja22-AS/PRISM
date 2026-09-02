import datetime
from storage.db import get_pg_session, neo4j_driver
from storage.models import Evidence

def process_evidence(normalized_data):
    """
    Upserts evidence into PostgreSQL and Neo4j.
    """
    db_gen = get_pg_session()
    db = next(db_gen)
    
    try:
        # 1. PostgreSQL Upsert
        existing = db.query(Evidence).filter(Evidence.id == normalized_data["id"]).first()
        if existing:
            if normalized_data["last_seen"]:
                existing.last_seen = datetime.datetime.fromisoformat(normalized_data["last_seen"].replace("Z", "+00:00")).replace(tzinfo=None)
            existing.last_scan = datetime.datetime.utcnow()
            existing.data = normalized_data["data"]
            db.commit()
            print(f"Updated existing evidence: {existing.id}")
        else:
            first_seen_dt = datetime.datetime.fromisoformat(normalized_data["first_seen"].replace("Z", "+00:00")).replace(tzinfo=None) if normalized_data.get("first_seen") else datetime.datetime.utcnow()
            last_seen_dt = datetime.datetime.fromisoformat(normalized_data["last_seen"].replace("Z", "+00:00")).replace(tzinfo=None) if normalized_data.get("last_seen") else datetime.datetime.utcnow()
            
            new_evidence = Evidence(
                id=normalized_data["id"],
                category=normalized_data["category"],
                source_id=normalized_data["source_id"],
                first_seen=first_seen_dt,
                last_seen=last_seen_dt,
                last_scan=datetime.datetime.utcnow(),
                reliability=normalized_data["reliability"],
                data=normalized_data["data"]
            )
            db.add(new_evidence)
            db.commit()
            print(f"Inserted new evidence: {new_evidence.id}")

        # 2. Neo4j Upsert (Persona and Evidence nodes)
        with neo4j_driver.session() as session:
            author = normalized_data["data"].get("author")
            ev_id = normalized_data["id"]
            
            if author:
                query = """
                MERGE (p:Persona {handle: $author})
                MERGE (e:Evidence {id: $ev_id})
                SET e.category = $category
                MERGE (p)-[:PRODUCED]->(e)
                """
                session.run(query, author=author, ev_id=ev_id, category=normalized_data["category"])
                print(f"Updated graph for Persona: {author}")
            
    except Exception as e:
        print(f"Error processing evidence: {e}")
        db.rollback()
    finally:
        db.close()
