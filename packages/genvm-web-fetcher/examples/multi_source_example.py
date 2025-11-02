"""
Multi-source Fallback Example

Demonstrates using WebFetcher for multiple data sources with fallback.

# { "Depends": "py-genlayer:latest" }
"""
import genlayer.gl as gl
from web_fetcher import WebFetcher


class MultiSourceOracle(gl.Contract):
    """Example using WebFetcher for multi-source data fetching"""
    
    def __init__(self):
        self.data = {}
        self.source = ""
    
    @gl.public.view
    def get_data(self) -> dict:
        return {
            "data": self.data,
            "source": self.source
        }
    
    @gl.public.write
    def fetch_data(self) -> None:
        fetcher = WebFetcher()
        
        def leader():
            # Try multiple sources
            sources = [
                "https://api.example.com/data",
                "https://backup.example.com/data",
                "https://fallback.example.com/data",
            ]
            
            for source_url in sources:
                try:
                    resp = fetcher.get(source_url)
                    data = fetcher.json(resp, source_url)
                    
                    # Validate data structure
                    if isinstance(data, dict) and "result" in data:
                        return {
                            "data": data,
                            "source": source_url
                        }
                except gl.vm.UserError:
                    continue  # Try next source
                except Exception:
                    continue
            
            raise gl.vm.UserError("All data sources failed")
        
        def validator(result):
            try:
                unpacked = gl.vm.unpack_result(result)
                return (
                    isinstance(unpacked, dict) and
                    "data" in unpacked and
                    "source" in unpacked
                )
            except Exception:
                return False
        
        result = gl.vm.run_nondet(leader, validator)
        self.data = result["data"]
        self.source = result["source"]

