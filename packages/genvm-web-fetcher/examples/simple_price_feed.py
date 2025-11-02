"""
Simple Price Feed Example using WebFetcher library

# { "Depends": "py-genlayer:latest" }
"""
import genlayer.gl as gl
from web_fetcher import PriceFeedPattern


class SimplePriceFeed(gl.Contract):
    """Simple contract that fetches ETH price using PriceFeedPattern"""
    
    def __init__(self):
        self.last_price = 0.0
        self.last_source = ""
    
    @gl.public.view
    def get_price(self) -> dict:
        return {
            "price": str(self.last_price),
            "source": self.last_source
        }
    
    @gl.public.write
    def update_price(self) -> None:
        pattern = PriceFeedPattern()
        
        def leader():
            price_data = pattern.get_price("ETH")
            return {
                "price": str(price_data["price"]),
                "source": price_data["source"]
            }
        
        def validator(result):
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                price_str = unpacked.get("price")
                if price_str:
                    price = float(price_str)
                    return price > 0
                return False
            except Exception:
                return False
        
        data = gl.vm.run_nondet(leader, validator)
        self.last_price = float(data["price"])
        self.last_source = str(data["source"])

