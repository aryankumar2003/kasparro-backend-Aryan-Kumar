
import os
import sys
sys.path.append(os.getcwd())

# Mock environment variables BEFORE importing config
os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/ingestion_db"
os.environ["API_KEY"] = "test-key"
os.environ["COIN_IDS"] = '["btc-bitcoin"]' # Fix potential parsing error if default missing
os.environ["COINGECKO_API_KEY"] = "mock-key"

import asyncio
from core.config import settings
from ingestion.orchestrator import Orchestrator
from ingestion.coingecko_source import CoinGeckoSource
from ingestion.csv_source import CSVSource

async def verify():
    print("--- Verifying Secrets ---")
    try:
        # Should rely on env vars now, so we can check if they are set in the environment or if pydantic complains if missing
        # We will manually check settings
        print(f"DB URL Set: {bool(settings.DATABASE_URL)}")
        print(f"API Key Set: {bool(settings.API_KEY)}")
    except Exception as e:
        print(f"Configuration Error (Expected if env vars missing): {e}")

    print("\n--- Verifying Data Sources ---")
    orchestrator = Orchestrator()
    print(f"Sources initialized: {len(orchestrator.sources)}")
    
    has_csv = any(isinstance(s, CSVSource) for s in orchestrator.sources)
    has_coingecko = any(isinstance(s, CoinGeckoSource) for s in orchestrator.sources)
    
    print(f"Has CSVSource: {has_csv}")
    print(f"Has CoinGeckoSource: {has_coingecko}")

    if not has_csv or not has_coingecko:
        print("FAIL: Missing required sources")
        return

    print("PASS: Sources present")

    print("\n--- Verifying Normalization (CoinGecko Simple/Price) ---")
    
    # Mock data as returned by CoinGeckoSource using simple/price endpoint
    mock_item = {
        "source": "coingecko",
        "external_id": "bitcoin",
        "symbol": "BTC", # This is injected by the source wrapper now
        "data": {
            "usd": 89815, 
            "usd_market_cap": 2000000, 
            "usd_24h_vol": 50000, 
            "last_updated_at": 1709251200, # Mock timestamp
            "symbol_injected": "BTC"
        }
    }
    
    unified = orchestrator._normalize(
        source="coingecko",
        external_id="bitcoin",
        data=mock_item["data"],
        raw_data=mock_item["data"]
    )
    
    if unified and unified.price == 89815 and unified.symbol == "BTC":
        print("PASS: CoinGecko normalization correct")
    else:
        print(f"FAIL: CoinGecko normalization failed {unified}")
        
    print("\n--- Verifying Canonical Normalization ---")
    # Check that "btc-bitcoin" -> "BTC"
    norm_unified = orchestrator._normalize(
        source="coinpaprika",
        external_id="btc-bitcoin",
        data={
            "symbol": "BTC", 
            "last_updated": "2024-01-01T00:00:00Z",
            "quotes": {"USD": {"price": 100, "volume_24h": 100, "market_cap": 100}}
        },
        raw_data={}
    )
    if norm_unified and norm_unified.symbol == "BTC":
        print("PASS: btc-bitcoin -> BTC")
    else:
        print(f"FAIL: Canonical normalization failed: {norm_unified.symbol if norm_unified else 'None'}")


if __name__ == "__main__":
    # Mock env vars for the test
    os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/ingestion_db"
    os.environ["API_KEY"] = "test-key"
    asyncio.run(verify())
