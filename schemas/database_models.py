from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from services.database import Base
from datetime import datetime

class RawData(Base):
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True) 
    external_id = Column(String, index=True) 
    data = Column(JSONB) 
    ingested_at = Column(DateTime, default=datetime.utcnow)

class UnifiedData(Base):
    __tablename__ = "unified_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    original_id = Column(String, index=True)
    symbol = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    timestamp = Column(DateTime, index=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSONB) 

class Checkpoint(Base):
    __tablename__ = "checkpoints"

    source_id = Column(String, primary_key=True, index=True)
    last_ingested_at = Column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="Running") 
    items_processed = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
