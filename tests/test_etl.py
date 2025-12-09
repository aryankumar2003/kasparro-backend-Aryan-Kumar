import pytest
from datetime import datetime
from ingestion.orchestrator import Orchestrator

def test_normalize_coinpaprika():
    orchestrator = Orchestrator()
    
    raw_data = {
        "symbol": "BTC",
        "last_updated": "2025-12-09T10:00:00Z",
        "quotes": {
            "USD": {
                "price": 90000.0,
                "volume_24h": 1000000.0,
                "market_cap": 2000000000.0
            }
        }
    }
    
    unified = orchestrator._normalize(
        source="coinpaprika",
        external_id="btc-bitcoin",
        data=raw_data,
        raw_data=raw_data
    )
    
    assert unified is not None
    assert unified.symbol == "BTC"
    assert unified.price == 90000.0
    assert unified.volume_24h == 1000000.0
    assert unified.original_id == "btc-bitcoin"
    assert isinstance(unified.timestamp, datetime)

def test_normalize_csv():
    orchestrator = Orchestrator()
    
    raw_data = {
        "symbol": "ETH",
        "price": "4000.0",
        "volume": "500000.0",
        "market_cap": "400000000.0"
    }
    
    unified = orchestrator._normalize(
        source="csv",
        external_id="eth-ethereum",
        data=raw_data,
        raw_data=raw_data
    )
    
    assert unified is not None
    assert unified.symbol == "ETH"
    assert unified.price == 4000.0
