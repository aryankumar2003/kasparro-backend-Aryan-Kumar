import logging
from typing import Dict, Any, List
import requests
from datetime import datetime
from ingestion.base import IngestionSource
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings

logger = logging.getLogger(__name__)

class CoinGeckoSource(IngestionSource):
    def __init__(self, coin_id: str):
  
        parts = coin_id.split("-", 1)
        self.symbol = parts[0].upper() if len(parts) > 0 else "UNKNOWN" 
        self.gecko_id = parts[1] if len(parts) > 1 else coin_id
        
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.api_key = settings.COINGECKO_API_KEY

    def __str__(self):
        return f"CoinGeckoSource({self.gecko_id})"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def ingest(self) -> List[Dict[str, Any]]:
        try:
            params = {
                "ids": self.gecko_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_last_updated_at": "true"
            }
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key

            response = requests.get(
                self.api_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Simple price endpoint returns dict keyed by coin id e.g. {"bitcoin": {...}}
            if self.gecko_id not in data:
                logger.warning(f"No data returned for {self.gecko_id}")
                return []

            coin_data = data[self.gecko_id]
            coin_data["symbol_injected"] = self.symbol
            
            return [{
                "source": "coingecko",
                "external_id": self.gecko_id,
                "data": coin_data,
                "ingested_at": datetime.utcnow().isoformat()
            }]
        except Exception as e:
            logger.error(f"Failed to fetch data from CoinGecko for {self.gecko_id}: {e}")
            raise e
