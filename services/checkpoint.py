import logging
from datetime import datetime
from typing import Optional
from services.database import SessionLocal
from schemas.database_models import Checkpoint

logger = logging.getLogger(__name__)

def load_checkpoint(source_id: str) -> Optional[datetime]:
    db = SessionLocal()
    try:
        checkpoint = db.query(Checkpoint).filter(Checkpoint.source_id == source_id).first()
        return checkpoint.last_ingested_at if checkpoint else None
    except Exception as e:
        logger.error(f"Failed to load checkpoint for {source_id}: {e}")
        return None
    finally:
        db.close()

def save_checkpoint(source_id: str, last_ingested_at: datetime):
    db = SessionLocal()
    try:
        checkpoint = db.query(Checkpoint).filter(Checkpoint.source_id == source_id).first()
        if checkpoint:
            checkpoint.last_ingested_at = last_ingested_at
        else:
            checkpoint = Checkpoint(source_id=source_id, last_ingested_at=last_ingested_at)
            db.add(checkpoint)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save checkpoint for {source_id}: {e}")
        db.rollback()
    finally:
        db.close()
