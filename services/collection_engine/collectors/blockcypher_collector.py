import os
import requests
from typing import List, Dict, Any
from .base import BaseCollector

class BlockcypherCollector(BaseCollector):
    def __init__(self, wallet_address: str):
        super().__init__(source_id="blockcypher")
        self.wallet_address = wallet_address
        self.api_key = os.getenv("BLOCKCYPHER_API_KEY", "")
        self.reliability = 0.99
        self.base_url = "https://api.blockcypher.com/v1/btc/main/addrs"
        
        # BlockCypher technically works without an API key for limited requests
        # but it's much better to have one.
        
    def fetch_data(self) -> Any:
        url = f"{self.base_url}/{self.wallet_address}/full"
        params = {}
        if self.api_key:
            params["token"] = self.api_key
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"BlockCypher API Error: {e}")
            return None

    def parse_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        if not raw_data:
            return []
        
        evidence = []
        
        # Extract balance
        balance = raw_data.get('balance', 0)
        evidence.append({
            "type": "WalletBalance",
            "value": balance,
            "confidence": 1.0
        })
        
        # Extract connected wallets from transactions
        txs = raw_data.get('txs', [])
        connected_wallets = set()
        
        for tx in txs[:10]: # Analyze top 10 recent transactions
            # Add inputs
            for inp in tx.get('inputs', []):
                for addr in inp.get('addresses', []):
                    if addr != self.wallet_address:
                        connected_wallets.add(addr)
            
            # Add outputs
            for out in tx.get('outputs', []):
                for addr in out.get('addresses', []):
                    if addr != self.wallet_address:
                        connected_wallets.add(addr)
                        
        for wallet in connected_wallets:
            evidence.append({
                "type": "ConnectedWallet",
                "value": wallet,
                "confidence": 0.95
            })

        return evidence
