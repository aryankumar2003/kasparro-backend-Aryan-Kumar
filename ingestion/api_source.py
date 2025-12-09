import aiohttp
import asyncio
import logging
from typing import List, Dict, Any
from ingestion.base import IngestionSource
from core.config import settings
from services.monitoring import increment_error
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class CoinPaprikaSource(IngestionSource):
    def __init__(self, coin_id: str):
        self.coin_id = coin_id
        self.endpoint = f"{settings.COINPAPRIKA_API_URL}/tickers/{coin_id}"
        self.base_url = settings.COINPAPRIKA_API_URL
        self.headers = {}
        if settings.COINPAPRIKA_API_KEY:
            self.headers["Authorization"] = settings.COINPAPRIKA_API_KEY

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True
    )
    async def _fetch_data(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Fetches data from the CoinPaprika API with retry logic.
        Raises aiohttp.ClientError on non-200 status codes.
        """
        async with session.get(self.endpoint, headers=self.headers) as response:
            response.raise_for_status()  
            return await response.json()

    async def ingest(self) -> List[Dict[str, Any]]:
        """
        Fetches ticker data for the specific coin.
        Returns a list containing a single dictionary with raw data.
        """
        results = []
        try:
            async with aiohttp.ClientSession() as session:
                data = await self._fetch_data(session)
                
                results.append({
                    "source": "coinpaprika",
                    "external_id": self.coin_id,
                    "data": data
                })
        except aiohttp.ClientResponseError as e:
            logger.error(f"CoinPaprika API request failed for {self.coin_id} (status: {e.status}): {e}")
            increment_error()
        except aiohttp.ClientError as e:
            logger.error(f"Network or client error ingesting from CoinPaprika {self.endpoint}: {e}")
            increment_error()
        except Exception as e:
            logger.error(f"Unexpected error ingesting from CoinPaprika {self.endpoint}: {e}")
            increment_error()
        
        return results
