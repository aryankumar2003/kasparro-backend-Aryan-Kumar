import asyncio
import logging
import uuid
from typing import List, Dict, Any
from datetime import datetime
from ingestion.base import IngestionSource
from ingestion.api_source import CoinPaprikaSource
from ingestion.coingecko_source import CoinGeckoSource
from ingestion.csv_source import CSVSource
from ingestion.rss_source import RSSSource
from core.config import settings
from services.database import SessionLocal
from schemas.database_models import RawData, UnifiedData, Job
from services.checkpoint import load_checkpoint, save_checkpoint
from services.monitoring import increment_ingested, increment_error, set_last_run_status
from core.normalization import SymbolNormalizer

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.sources: List[IngestionSource] = []
        self._setup_sources()

    def _setup_sources(self):
        
        for coin_id in settings.COIN_IDS:
            self.sources.append(CoinPaprikaSource(coin_id))
        
        
        
     
        for url in settings.RSS_FEEDS:
            self.sources.append(RSSSource(url))

        
        # CSV Source
        self.sources.append(CSVSource("data/sample_data.csv"))
        
        # CoinGecko Source
        for coin_id in settings.COIN_IDS:
             self.sources.append(CoinGeckoSource(coin_id))

    async def run(self, simulate_failure: bool = False):
        run_id = str(uuid.uuid4())
        logger.info(f"Starting ingestion run {run_id}...")
        set_last_run_status("Running")
        
        
        db = SessionLocal()
        job = Job(run_id=run_id, status="Running")
        db.add(job)
        db.commit()
        db.refresh(job) # Need ID if we want to update later, though we close DB here for the loop
        db.close()
        
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
                        
                        # Process in thread pool to avoid blocking async loop with synchronous DB calls
                        processed = await asyncio.to_thread(self._process_item_wrapper, item)
                        
                        if processed:
                            items_processed += 1
                    
                    logger.info(f"Processed items from {source}")
                except Exception as e:
                    logger.error(f"Error processing source {source}: {e}")
                    error_count += 1
                    increment_error()
                    if simulate_failure: 
                         raise e
            
            # Update job status in new session
            self._update_job_status(run_id, "Completed", items_processed, error_count)
            set_last_run_status("Completed")
        except Exception as e:
            logger.error(f"Critical error in orchestrator: {e}")
            self._update_job_status(run_id, "Failed", items_processed, error_count)
            set_last_run_status("Failed")
        finally:
            logger.info(f"Ingestion run {run_id} finished.")
        logger.info(f"Ingestion run {run_id} completed.")

    def _detect_schema_drift(self, item: Dict[str, Any]):
        source = item["source"]
        data = item["data"]
        
        
        expected_keys = set()
        if source == "coinpaprika":
            expected_keys = {"id", "name", "symbol", "rank", "last_updated", "quotes"}
        elif source == "coingecko":
            expected_keys = {"usd", "usd_market_cap", "usd_24h_vol", "last_updated_at", "symbol_injected"}
        elif source == "rss":
            expected_keys = {"title", "link", "summary", "description", "published", "published_parsed", "author", "tags"}
        elif source == "csv":
            expected_keys = {"symbol", "price", "volume", "market_cap"}
        
        if expected_keys:
            actual_keys = set(data.keys())
            unexpected = actual_keys - expected_keys
            if unexpected:
                logger.warning(f"Schema Drift Detected for {source}: Unexpected keys {unexpected}")
            
            missing = expected_keys - actual_keys
            if missing:
                logger.warning(f"Schema Drift Detected for {source}: Missing keys {missing}")

    def _process_item_wrapper(self, item: Dict[str, Any]) -> bool:
        """Wrapper to handle session creation for each item processing."""
        db = SessionLocal()
        try:
             return self._process_item(db, item)
        except Exception as e:
            logger.error(f"Error in process_item: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def _process_item(self, db, item: Dict[str, Any]) -> bool:
        source = item["source"]
        # Allow multiple rows if IDs differ, but check if we already have this exact data?
        # For now, just insert RawData. logic kept same, but normalization improved.
        
        external_id = item["external_id"]
        data = item["data"]

        raw_record = RawData(
            source=source,
            external_id=external_id,
            data=data,
            ingested_at=datetime.utcnow()
        )
        db.add(raw_record)
        db.commit() # Commit to get ID and ensure raw data is saved
        
        # Use raw_record.data in case DB added defaults or modified it (unlikely for JSONB but good practice)
        unified_record = self._normalize(source, external_id, data, raw_record.data)
        
        if unified_record:
            db.add(unified_record)
            db.commit()
            increment_ingested()
            return True
        return False

    def _update_job_status(self, run_id: str, status: str, items: int, errors: int):
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.run_id == run_id).first()
            if job:
                job.status = status
                job.items_processed = items
                job.error_count = errors
                job.end_time = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
        finally:
            db.close()

    def _normalize(self, source: str, external_id: str, data: Dict[str, Any], raw_data: Any) -> UnifiedData:
        try:
            # Common extraction
            symbol_raw = None
            price_val = None
            volume_val = None
            market_cap_val = None
            timestamp_val = datetime.utcnow()
            
            if source == "coinpaprika":
                quotes = data.get("quotes", {}).get("USD", {})
                last_updated_str = data.get("last_updated")
                timestamp = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%SZ") if last_updated_str else datetime.utcnow()
                
                symbol = data.get("symbol")
                price = quotes.get("price")
                
                if not symbol or price is None:
                    raise ValueError("Missing required fields: symbol or price")
                
                symbol_raw = symbol
                price_val = price
                volume_val = quotes.get("volume_24h")
                market_cap_val = quotes.get("market_cap")
                timestamp_val = timestamp

            elif source == "coingecko":
    
                current_price = data.get("usd")
                total_volume = data.get("usd_24h_vol")
                market_cap = data.get("usd_market_cap")
                last_updated_at = data.get("last_updated_at")
                
                timestamp = datetime.utcfromtimestamp(last_updated_at) if last_updated_at else datetime.utcnow()
                

                
                symbol = data.get("symbol_injected") 
                
                symbol_raw = symbol
                price_val = current_price
                volume_val = total_volume
                market_cap_val = market_cap
                timestamp_val = timestamp

            elif source == "rss":
                
                
                
                published_parsed = data.get("published_parsed")
                timestamp = datetime(*published_parsed[:6]) if published_parsed else datetime.utcnow()
                
                
                timestamp_val = timestamp
            

            elif source == "csv":
                symbol_raw = data.get("symbol")
                price_val = float(data.get("price", 0))
                volume_val = float(data.get("volume", 0))
                market_cap_val = float(data.get("market_cap", 0))
            
            canonical_symbol = SymbolNormalizer.get_canonical_symbol(external_id, symbol_raw)
            
            return UnifiedData(
                source=source,
                original_id=external_id,
                symbol=canonical_symbol,
                price=price_val,
                volume_24h=volume_val,
                market_cap=market_cap_val,
                timestamp=timestamp_val,
                raw_data=raw_data
            )
        except Exception as e:
            logger.error(f"Normalization error for {source} {external_id}: {e}")
            return None
        return None
