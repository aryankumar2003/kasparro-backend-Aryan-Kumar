from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IngestionSource(ABC):
    @abstractmethod
    async def ingest(self) -> List[Dict[str, Any]]:
        """
        Fetch data from the source and return a list of raw data dictionaries.
        Each dict should have: source, external_id, data (JSON serializable).
        """
        pass
