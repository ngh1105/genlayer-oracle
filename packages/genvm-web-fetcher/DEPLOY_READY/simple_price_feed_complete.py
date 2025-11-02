# { "Depends": "py-genlayer:latest" }

import json
import genlayer.gl as gl


# ============================================================================
# WebFetcher Library (embedded)
# ============================================================================

class WebFetcher:
    """Core web fetcher with utility methods for common HTTP operations."""
    
    def ensure_body_bytes(self, resp, name: str) -> str:
        if resp.body is None:
            raise gl.vm.UserError(f"{name}: empty body")
        try:
            return resp.body.decode("utf-8")
        except Exception:
            raise gl.vm.UserError(f"{name}: body decode error")
    
    def json(self, resp, name: str) -> dict:
        text = self.ensure_body_bytes(resp, name)
        try:
            return json.loads(text)
        except Exception:
            raise gl.vm.UserError(f"{name}: json parse error")
    
    def ensure_status(self, resp, expected_status: int = 200, name: str = "response") -> None:
        if not resp or not hasattr(resp, 'status'):
            raise gl.vm.UserError(f"{name}: invalid response")
        if resp.status != expected_status:
            raise gl.vm.UserError(f"{name}: http {resp.status}")
    
    def get(self, url: str, headers: dict = None, expected_status: int = 200) -> any:
        try:
            if headers is None:
                headers = {"User-Agent": "GenVM-WebFetcher/1.0"}
            
            resp = gl.nondet.web.get(url, headers=headers)
            self.ensure_status(resp, expected_status, url)
            return resp
        except gl.vm.UserError:
            raise
        except Exception as e:
            raise gl.vm.UserError(f"GET {url}: {str(e)}")
    
    def to_float(self, name: str, val) -> float:
        try:
            return float(val)
        except Exception:
            raise gl.vm.UserError(f"{name}: parse float error")


class PriceFeedPattern:
    """Pre-built pattern for cryptocurrency price feeds."""
    
    def __init__(self):
        self.fetcher = WebFetcher()
    
    def get_price(self, symbol: str, binance_hosts: list = None, coingecko_fallback: bool = True) -> dict:
        """Get cryptocurrency price with multi-source fallback."""
        if binance_hosts is None:
            binance_hosts = [
                "https://api.binance.com",
                "https://api-gcp.binance.com",
                "https://api1.binance.com",
                "https://api2.binance.com",
                "https://api3.binance.com",
                "https://api4.binance.com",
            ]
        
        price = None
        price_source = None
        
        # Try Binance mirrors
        for host in binance_hosts:
            try:
                url = f"{host}/api/v3/ticker/price?symbol={symbol}USDT"
                resp = self.fetcher.get(url)
                data = self.fetcher.json(resp, f"binance-{host}")
                
                price_str = data.get("price") if isinstance(data, dict) else None
                if price_str is not None:
                    price = self.fetcher.to_float("binance price", price_str)
                    price_source = "binance"
                    break
            except gl.vm.UserError:
                continue
            except Exception:
                continue
        
        # Fallback to Coingecko
        if price is None and coingecko_fallback:
            try:
                symbol_lower = symbol.lower()
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_lower}&vs_currencies=usd"
                resp = self.fetcher.get(url)
                data = self.fetcher.json(resp, "coingecko")
                
                asset_data = data.get(symbol_lower) if isinstance(data, dict) else None
                if asset_data and isinstance(asset_data, dict):
                    usd_val = asset_data.get("usd")
                    if usd_val is not None:
                        price = self.fetcher.to_float("coingecko price", usd_val)
                        price_source = "coingecko"
            except Exception:
                pass
        
        if price is None or price <= 0 or price_source is None:
            raise gl.vm.UserError(f"all price sources failed for {symbol}")
        
        return {"price": price, "source": price_source}


# ============================================================================
# Simple Price Feed Contract
# ============================================================================

class SimplePriceFeed(gl.Contract):
    """
    Simple contract that fetches ETH price using PriceFeedPattern.
    
    Demonstrates WebFetcher library usage for price feeds with multi-source fallback.
    """
    
    # CRITICAL: All persistent fields MUST be declared in class body with type annotations
    # Fields assigned only in __init__ are NOT persistent!
    last_price: float
    last_source: str
    
    def __init__(self):
        self.last_price = 0.0
        self.last_source = ""
    
    @gl.public.view
    def debug_state(self) -> dict:
        """Debug method to check state persistence."""
        # Initialize if not exists
        if not hasattr(self, 'last_price'):
            self.last_price = 0.0
        if not hasattr(self, 'last_source'):
            self.last_source = ""
        
        return {
            "has_price": hasattr(self, 'last_price'),
            "price_value": str(self.last_price),
            "price_type": type(self.last_price).__name__,
            "has_source": hasattr(self, 'last_source'),
            "source_value": self.last_source,
            "contract_address": str(self.address) if hasattr(self, 'address') else 'NO_ADDRESS',
        }
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price and source."""
        # Initialize attributes if they don't exist (shouldn't happen if __init__ ran)
        if not hasattr(self, 'last_price'):
            self.last_price = 0.0
        if not hasattr(self, 'last_source'):
            self.last_source = ""
        
        # Directly read and return - don't use getattr to ensure we're reading from actual state
        return {
            "price": str(self.last_price),
            "source": self.last_source
        }
    
    @gl.public.write
    def update_price(self) -> None:
        """
        Fetch and update ETH price using PriceFeedPattern.
        
        Uses non-deterministic execution with leader-validator consensus.
        Fetches from Binance (multiple mirrors) with Coingecko fallback.
        """
        pattern = PriceFeedPattern()
        
        def leader():
            """Leader function: Fetches price from APIs."""
            price_data = pattern.get_price("ETH")
            # Return as flat dict - run_nondet returns this directly
            return {
                "price": str(price_data["price"]),
                "source": price_data["source"]
            }
        
        def validator(result):
            """Validator function: Verifies price data is valid."""
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                price_str = unpacked.get("price")
                if price_str:
                    price = float(price_str)
                    # Validate: price should be positive and reasonable
                    return price > 0 and price < 100000  # ETH reasonable range
                return False
            except Exception:
                return False
        
        # Run non-deterministic execution with consensus
        # Match exactly with oracle_consumer.py pattern
        try:
            data = gl.vm.run_nondet(leader, validator)
        except gl.vm.UserError:
            raise  # Re-raise UserError
        except gl.vm.VMError as e:
            raise gl.vm.UserError(f"VM error in run_nondet: {str(e)}")
        except Exception as e:
            raise gl.vm.UserError(f"run_nondet error: {str(e)}")
        
        # Validate result format
        if not isinstance(data, dict):
            raise gl.vm.UserError("invalid result format")
        
        price_str = data.get("price")
        source_str = data.get("source")
        
        if price_str is None or source_str is None:
            raise gl.vm.UserError("missing price or source in result")
        
        # Parse and assign - EXACTLY like oracle_consumer.py
        try:
            # Parse string to float and assign - ensure persistence
            price_float = float(str(price_str))
            self.last_price = price_float
            # Force storage write by reassigning (exact pattern from oracle_consumer)
            _ = self.last_price
        except (ValueError, TypeError):
            raise gl.vm.UserError(f"invalid price value: {price_str}")
        
        source_str_final = str(source_str)
        self.last_source = source_str_final
        _ = self.last_source
