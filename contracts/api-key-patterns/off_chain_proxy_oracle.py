# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
Oracle Contract using Off-chain Proxy Pattern

The contract calls a proxy service that holds API keys.
Keys never appear in contract code or on-chain.

Architecture:
  Contract → Proxy Service (holds keys) → External API → Proxy → Contract

Benefits:
  - Maximum security: Keys never exposed on-chain
  - Easy key rotation: Update keys in proxy without contract changes
  - Centralized rate limit control

Trade-offs:
  - Requires trusted proxy service (centralization)
  - Proxy service must be reliable (single point of failure)
"""
import json
import genlayer.gl as gl


class ProxyOracle(gl.Contract):
    """
    Oracle that uses off-chain proxy for API key management.
    
    The contract makes HTTP requests to a proxy service.
    The proxy service holds API keys and makes authenticated requests.
    """
    
    # Persistent state
    last_price: float
    last_source: str
    proxy_url: str  # Proxy service URL (configured at deployment)
    
    def __init__(self):
        # Initialize state
        self.last_price = 0.0
        self.last_source = ""
        # Default proxy URL (can be updated via set_proxy_url)
        # In production, set this via deployment or constructor parameter
        self.proxy_url = "https://your-proxy-service.com/api"
    
    @gl.public.write
    def set_proxy_url(self, url: str) -> None:
        """Update proxy service URL."""
        self.proxy_url = str(url)
        _ = self.proxy_url
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price."""
        return {
            "price": str(self.last_price),
            "source": self.last_source,
            "proxy_url": self.proxy_url
        }
    
    @gl.public.write
    def update_price(self, symbol: str = "ETH") -> None:
        """
        Fetch price via proxy service.
        
        The proxy service handles API key authentication.
        Contract never sees or stores API keys.
        
        Args:
            symbol: Cryptocurrency symbol (default: "ETH")
        """
        def leader():
            """Leader fetches data via proxy (proxy has API keys)."""
            # Ensure proxy URL is set
            if not self.proxy_url or self.proxy_url == "":
                raise gl.vm.UserError("proxy url not configured")
            
            # Call proxy service
            # Proxy adds API key headers internally
            proxy_endpoint = f"{self.proxy_url}/price/{symbol.upper()}"
            
            try:
                proxy_response = gl.nondet.web.get(
                    proxy_endpoint,
                    headers={
                        "User-Agent": "GenLayerOracle/1.0",
                        "Content-Type": "application/json",
                        # NO API KEY HERE - Proxy handles it
                    }
                )
            except Exception as e:
                raise gl.vm.UserError(f"proxy request failed: {str(e)}")
            
            # Validate response
            if not proxy_response or not hasattr(proxy_response, 'status'):
                raise gl.vm.UserError("proxy service unavailable")
            
            if proxy_response.status != 200:
                error_body = ""
                if proxy_response.body:
                    try:
                        error_body = proxy_response.body.decode("utf-8")
                    except:
                        pass
                raise gl.vm.UserError(
                    f"proxy error {proxy_response.status}: {error_body[:100]}"
                )
            
            # Parse response
            if not proxy_response.body:
                raise gl.vm.UserError("proxy response empty")
            
            try:
                body_text = proxy_response.body.decode("utf-8")
                data = json.loads(body_text)
            except Exception as e:
                raise gl.vm.UserError(f"proxy response parse error: {str(e)}")
            
            # Extract price
            price_str = data.get("price")
            source = data.get("source", "proxy")
            
            if price_str is None:
                raise gl.vm.UserError("invalid proxy response: price missing")
            
            try:
                price = float(str(price_str))
                if price <= 0:
                    raise gl.vm.UserError(f"invalid price: {price}")
            except (ValueError, TypeError) as e:
                raise gl.vm.UserError(f"price parse error: {str(e)}")
            
            return {
                "price": str(price),
                "source": str(source),
                "symbol": symbol.upper()
            }
        
        def validator(result):
            """Validate proxy response format and value."""
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                
                price_str = unpacked.get("price")
                if price_str is None:
                    return False
                
                # Validate price is positive and reasonable
                try:
                    price = float(price_str)
                    # Reasonable range for crypto prices
                    return price > 0 and price < 100000
                except (ValueError, TypeError):
                    return False
                
            except Exception:
                return False
        
        # Run consensus
        try:
            data = gl.vm.run_nondet(leader, validator)
        except gl.vm.UserError:
            raise  # Re-raise UserError as-is
        except Exception as e:
            raise gl.vm.UserError(f"update_price failed: {str(e)}")
        
        # Validate and update state
        if not isinstance(data, dict):
            raise gl.vm.UserError("invalid result format")
        
        price_str = data.get("price")
        source_str = data.get("source", "proxy")
        
        if price_str is None:
            raise gl.vm.UserError("missing price in result")
        
        try:
            price_float = float(str(price_str))
            self.last_price = price_float
            _ = self.last_price  # Force persistence
        except (ValueError, TypeError) as e:
            raise gl.vm.UserError(f"price assignment error: {str(e)}")
        
        self.last_source = str(source_str)
        _ = self.last_source  # Force persistence

