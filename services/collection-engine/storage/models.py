from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    source_type = Column(String)  # e.g., 'dark_web_forum', 'marketplace', 'authorized_dataset'
    url = Column(String)
    reliability_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Evidence(Base):
    __tablename__ = 'evidence'

    id = Column(String, primary_key=True)
    category = Column(String, nullable=False) # e.g., 'Identity', 'Network', 'Stylometry'
    source_id = Column(String)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    last_scan = Column(DateTime, default=datetime.utcnow)
    reliability = Column(Float, default=1.0)
    data = Column(JSON) # Flexible storage for raw extracted JSON footprints
