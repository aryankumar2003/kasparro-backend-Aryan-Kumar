import pytest
from datetime import datetime
from services.checkpoint import save_checkpoint, load_checkpoint
from schemas.database_models import Job
from ingestion.orchestrator import Orchestrator

def test_checkpoint_logic(db_session):
    pass 

def test_rss_normalization():
    orchestrator = Orchestrator()
    raw_data = {
        "title": "Test News",
        "link": "http://test.com/news",
        "published_parsed": (2025, 12, 9, 10, 0, 0, 0, 0, 0)
    }
    
    unified = orchestrator._normalize(
        source="rss",
        external_id="http://test.com/news",
        data=raw_data,
        raw_data=raw_data
    )
    
    assert unified.timestamp.year == 2025
    assert unified.source == "rss"

def test_job_tracking(db_session):
    
    job = Job(run_id="test-run", status="Completed", items_processed=10)
    db_session.add(job)
    db_session.commit()
    
    saved_job = db_session.query(Job).filter(Job.run_id == "test-run").first()
    assert saved_job.items_processed == 10
    assert saved_job.status == "Completed"
