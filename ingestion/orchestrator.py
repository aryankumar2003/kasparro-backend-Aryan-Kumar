import asyncio
import logging
import uuid
from typing import List, Dict, Any
from datetime import datetime
from ingestion.base import IngestionSource
from ingestion.api_source import CoinPaprikaSource
from ingestion.csv_source import CSVSource
from ingestion.rss_source import RSSSource
from core.config import settings
from services.database import SessionLocal
from schemas.database_models import RawData, UnifiedData, Job
from services.checkpoint import load_checkpoint, save_checkpoint
from services.monitoring import increment_ingested, increment_error, set_last_run_status

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.sources: List[IngestionSource] = []
        self._setup_sources()

    def _setup_sources(self):
        
        for coin_id in settings.COIN_IDS:
            self.sources.append(CoinPaprikaSource(coin_id))
        
        
        
        
        rss_feeds = ["http://feeds.bbci.co.uk/news/rss.xml"] 
        for url in rss_feeds:
            self.sources.append(RSSSource(url))

        
        

    async def run(self, simulate_failure: bool = False):
        run_id = str(uuid.uuid4())
        logger.info(f"Starting ingestion run {run_id}...")
        set_last_run_status("Running")
        
        db = SessionLocal()
        job = Job(run_id=run_id, status="Running")
        db.add(job)
        db.commit()
        
        items_processed = 0
        error_count = 0

        try:
            for source in self.sources:
                try:
                    if simulate_failure and items_processed > 0:
                        raise Exception("Simulated Failure Injection")

                    raw_items = await source.ingest()
                    if not raw_items:
                        continue
                    
                    for item in raw_items:
                        
                        self._detect_schema_drift(item)
                        
                        if await self._process_item(db, item):
                            items_processed += 1
                    
                    db.commit()
                    logger.info(f"Processed items from {source}")
                except Exception as e:
                    logger.error(f"Error processing source {source}: {e}")
                    error_count += 1
                    increment_error()
                    db.rollback()
                    if simulate_failure: 
                         raise e
            
            job.status = "Completed"
            set_last_run_status("Completed")
        except Exception as e:
            logger.error(f"Critical error in orchestrator: {e}")
            job.status = "Failed"
            set_last_run_status("Failed")
        finally:
            job.end_time = datetime.utcnow()
            job.items_processed = items_processed
            job.error_count = error_count
            db.commit()
            db.close()
        logger.info(f"Ingestion run {run_id} completed.")

    def _detect_schema_drift(self, item: Dict[str, Any]):
        source = item["source"]
        data = item["data"]
        
        
        expected_keys = set()
        if source == "coinpaprika":
            expected_keys = {"id", "name", "symbol", "rank", "last_updated", "quotes"}
        elif source == "rss":
            expected_keys = {"title", "link", "summary", "description", "published", "published_parsed", "author", "tags"}
        
        if expected_keys:
            actual_keys = set(data.keys())
            unexpected = actual_keys - expected_keys
            if unexpected:
                logger.warning(f"Schema Drift Detected for {source}: Unexpected keys {unexpected}")
            
            missing = expected_keys - actual_keys
            if missing:
                logger.warning(f"Schema Drift Detected for {source}: Missing keys {missing}")

    async def _process_item(self, db, item: Dict[str, Any]) -> bool:
        source = item["source"]
        external_id = item["external_id"]
        data = item["data"]

        
        existing = db.query(RawData).filter(RawData.source == source, RawData.external_id == external_id).first()
        if existing:
            
            
            
            if source != "coinpaprika":
                return False

        raw_record = RawData(
            source=source,
            external_id=external_id,
            data=data,
            ingested_at=datetime.utcnow()
        )
        db.add(raw_record)
        db.flush()

        unified_record = self._normalize(source, external_id, data, raw_record.data)
        if unified_record:
            db.add(unified_record)
            increment_ingested()
            return True
        return False

    def _normalize(self, source: str, external_id: str, data: Dict[str, Any], raw_data: Any) -> UnifiedData:
        try:
            if source == "coinpaprika":
                quotes = data.get("quotes", {}).get("USD", {})
                last_updated_str = data.get("last_updated")
                timestamp = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%SZ") if last_updated_str else datetime.utcnow()
                
                symbol = data.get("symbol")
                price = quotes.get("price")
                
                if not symbol or price is None:
                    raise ValueError("Missing required fields: symbol or price")

                return UnifiedData(
                    source=source,
                    original_id=external_id,
                    symbol=symbol,
                    price=price,
                    volume_24h=quotes.get("volume_24h"),
                    market_cap=quotes.get("market_cap"),
                    timestamp=timestamp,
                    raw_data=raw_data
                )
            elif source == "rss":
                
                
                
                published_parsed = data.get("published_parsed")
                timestamp = datetime(*published_parsed[:6]) if published_parsed else datetime.utcnow()
                
                return UnifiedData(
                    source=source,
                    original_id=external_id,
                    symbol=None, 
                    price=None,
                    volume_24h=None,
                    market_cap=None,
                    timestamp=timestamp,
                    raw_data=raw_data
                )
            elif source == "csv":
                return UnifiedData(
                    source=source,
                    original_id=external_id,
                    symbol=data.get("symbol"),
                    price=float(data.get("price", 0)),
                    volume_24h=float(data.get("volume", 0)),
                    market_cap=float(data.get("market_cap", 0)),
                    timestamp=datetime.utcnow(),
                    raw_data=raw_data
                )
        except Exception as e:
            logger.error(f"Normalization error for {source} {external_id}: {e}")
            return None
        return None
