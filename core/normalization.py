from typing import Optional

class SymbolNormalizer:
    # Canonical mapping: Input -> Canonical Symbol
    _MAPPING = {
        # Bitcoin
        "btc-bitcoin": "BTC",
        "bitcoin": "BTC",
        "btc": "BTC",
        "BTC": "BTC",
        
        # Ethereum
        "eth-ethereum": "ETH",
        "ethereum": "ETH",
        "eth": "ETH",
        "ETH": "ETH",
        
        # Solana
        "sol-solana": "SOL",
        "solana": "SOL",
        "sol": "SOL",
        "SOL": "SOL",
        
        # Cardano
        "ada-cardano": "ADA",
        "cardano": "ADA",
        "ada": "ADA",
        "ADA": "ADA",
    }

    @classmethod
    def get_canonical_symbol(cls, input_id: str, input_symbol: Optional[str] = None) -> str:
       
        if input_symbol and input_symbol in cls._MAPPING:
            return cls._MAPPING[input_symbol]
            
        if input_id and input_id in cls._MAPPING:
            return cls._MAPPING[input_id]
            
        # Fallback
        return (input_symbol or input_id or "UNKNOWN").upper()
