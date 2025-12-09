import csv
import logging
import os
from typing import List, Dict, Any
from ingestion.base import IngestionSource
from services.monitoring import increment_error

logger = logging.getLogger(__name__)

class CSVSource(IngestionSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def ingest(self) -> List[Dict[str, Any]]:
        results = []
        if not os.path.exists(self.file_path):
            logger.error(f"CSV file not found: {self.file_path}")
            increment_error()
            return results

        try:
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    
                    external_id = row.get("id") or row.get("symbol") or f"csv_row_{reader.line_num}"
                    
                    results.append({
                        "source": "csv",
                        "external_id": external_id,
                        "data": row
                    })
        except Exception as e:
            logger.error(f"Error reading CSV {self.file_path}: {e}")
            increment_error()
            
        return results
