from ingestion.orchestrator import Orchestrator

def test_normalize_invalid_data():
    orchestrator = Orchestrator()
    
    
    raw_data = {
        "symbol": "BTC"
        
    }
    
    unified = orchestrator._normalize(
        source="coinpaprika",
        external_id="btc-bitcoin",
        data=raw_data,
        raw_data=raw_data
    )
    
    assert unified is None
