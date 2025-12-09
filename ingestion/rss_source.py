import feedparser
import logging
from typing import List, Dict, Any
from datetime import datetime
from ingestion.base import IngestionSource
from services.monitoring import increment_error

logger = logging.getLogger(__name__)

class RSSSource(IngestionSource):
    def __init__(self, feed_url: str):
        self.feed_url = feed_url

    async def ingest(self) -> List[Dict[str, Any]]:
        results = []
        try:
            feed = feedparser.parse(self.feed_url)
            if feed.bozo:
                logger.error(f"Error parsing RSS feed {self.feed_url}: {feed.bozo_exception}")
                increment_error()
                return results

            for entry in feed.entries:
                
                external_id = entry.get("link") or entry.get("id")
                
                
                
                entry_data = {
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "summary": entry.get("summary"),
                    "description": entry.get("description"),
                    "published": entry.get("published"),
                    "published_parsed": entry.get("published_parsed"), 
                    "author": entry.get("author"),
                    "tags": [t.term for t in entry.get("tags", [])]
                }

                results.append({
                    "source": "rss",
                    "external_id": external_id,
                    "data": entry_data
                })
        except Exception as e:
            logger.error(f"Error ingesting from RSS {self.feed_url}: {e}")
            increment_error()
            
        return results
