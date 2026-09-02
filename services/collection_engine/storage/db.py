import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storage.models import Base
from neo4j import GraphDatabase

# PostgreSQL setup
PG_USER = os.getenv("POSTGRES_USER", "prism_user")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "prism_password")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "prism_db")

PG_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(PG_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

# Neo4j setup
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "prism_password")

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def get_pg_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
