from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class QuoteUSD(BaseModel):
    price: float
    volume_24h: float
    market_cap: float
    percent_change_24h: float
    ath_price: float

class Quotes(BaseModel):
    USD: QuoteUSD

class CoinTicker(BaseModel):
    id: str
    name: str
    symbol: str
    rank: int
    last_updated: datetime
    quotes: Quotes


class UnifiedDataCreate(BaseModel):
    source: str
    original_id: str
    symbol: Optional[str] = None
    price: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: datetime
    raw_data: Dict[str, Any]

class UnifiedDataResponse(UnifiedDataCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationMetadata(BaseModel):
    total: int
    skip: int
    limit: int

class APIResponse(BaseModel):
    request_id: str
    api_latency_ms: float
    data: List[UnifiedDataResponse]
    meta: PaginationMetadata
