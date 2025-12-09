from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import time
import uuid
from services.database import get_db, engine
from schemas.models import APIResponse, UnifiedDataResponse, PaginationMetadata
from schemas.database_models import UnifiedData
from ingestion.orchestrator import Orchestrator
from services.monitoring import get_metrics
from api.auth import get_api_key

router = APIRouter(dependencies=[Depends(get_api_key)])

@router.post("/ingest", status_code=202)
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Trigger the ingestion process in the background.
    """
    orchestrator = Orchestrator()
    background_tasks.add_task(orchestrator.run)
    return {"message": "Ingestion started in background"}

@router.get("/data", response_model=APIResponse)
def read_data(
    skip: int = 0, 
    limit: int = 100, 
    symbol: Optional[str] = None, 
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve unified data with pagination and filtering.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    query = db.query(UnifiedData)
    if symbol:
        query = query.filter(UnifiedData.symbol == symbol)
    if source:
        query = query.filter(UnifiedData.source == source)
    
    total = query.count()
    data = query.order_by(UnifiedData.timestamp.desc()).offset(skip).limit(limit).all()
    
    latency = (time.time() - start_time) * 1000
    
    return APIResponse(
        request_id=request_id,
        api_latency_ms=latency,
        data=data,
        meta=PaginationMetadata(total=total, skip=skip, limit=limit)
    )

@router.get("/runs")
def list_runs(limit: int = 10, db: Session = Depends(get_db)):
    """
    List recent ETL runs.
    """
    from schemas.database_models import Job
    return db.query(Job).order_by(Job.start_time.desc()).limit(limit).all()

@router.get("/compare-runs")
def compare_runs(run_id_1: str, run_id_2: str, db: Session = Depends(get_db)):
    """
    Compare statistics between two runs.
    """
    from schemas.database_models import Job
    job1 = db.query(Job).filter(Job.run_id == run_id_1).first()
    job2 = db.query(Job).filter(Job.run_id == run_id_2).first()
    
    if not job1 or not job2:
        raise HTTPException(status_code=404, detail="One or both runs not found")
    
    return {
        "run_1": {
            "id": job1.run_id,
            "items": job1.items_processed,
            "errors": job1.error_count,
            "duration": (job1.end_time - job1.start_time).total_seconds() if job1.end_time else None
        },
        "run_2": {
            "id": job2.run_id,
            "items": job2.items_processed,
            "errors": job2.error_count,
            "duration": (job2.end_time - job2.start_time).total_seconds() if job2.end_time else None
        },
        "diff": {
            "items": job2.items_processed - job1.items_processed,
            "errors": job2.error_count - job1.error_count
        }
    }

@router.get("/stats")
def read_stats(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get ETL job history and statistics.
    """
    from schemas.database_models import Job
    jobs = db.query(Job).order_by(Job.start_time.desc()).limit(limit).all()
    return jobs

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Reports DB connectivity and ETL last-run status.
    """
    
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Health check DB error: {e}")
        db_status = "disconnected"
    
    
    metrics = get_metrics()
    
    return {
        "database": db_status,
        "etl_last_run_status": metrics.last_run_status,
        "etl_last_run_time": metrics.last_run_time,
        "metrics": metrics
    }
