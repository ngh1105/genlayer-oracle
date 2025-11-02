# { "Depends": "py-genlayer:latest" }
"""
GenVM Web Fetcher Library

A reusable library for fetching data from external APIs in GenVM Python contracts.
Provides error handling, multi-source fallback, and common patterns.

"""
import json
import genlayer.gl as gl


class WebFetcher:
    """
    Core web fetcher with utility methods for common HTTP operations.
    
    Provides error handling and response parsing utilities for GenVM contracts.
    """
    
    def ensure_body_bytes(self, resp, name: str) -> str:
        """
        Ensure response has body and decode to string.
        
        Args:
            resp: HTTP response object
            name: Name for error messages
            
        Returns:
            Decoded response body as string
            
        Raises:
            gl.vm.UserError: If body is missing or decode fails
        """
        if resp.body is None:
            raise gl.vm.UserError(f"{name}: empty body")
        try:
            return resp.body.decode("utf-8")
        except Exception:
            raise gl.vm.UserError(f"{name}: body decode error")
    
    def json(self, resp, name: str) -> dict:
        """
        Parse JSON response with error handling.
        
        Args:
            resp: HTTP response object
            name: Name for error messages
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            gl.vm.UserError: If JSON parsing fails
        """
        text = self.ensure_body_bytes(resp, name)
        try:
            return json.loads(text)
        except Exception:
            raise gl.vm.UserError(f"{name}: json parse error")
    
    def text(self, resp, name: str) -> str:
        """
        Get response text with error handling.
        
        Args:
            resp: HTTP response object
            name: Name for error messages
            
        Returns:
            Response body as string
        """
        return self.ensure_body_bytes(resp, name)
    
    def ensure_status(self, resp, expected_status: int = 200, name: str = "response") -> None:
        """
        Validate HTTP status code.
        
        Args:
            resp: HTTP response object
            expected_status: Expected status code (default: 200)
            name: Name for error messages
            
        Raises:
            gl.vm.UserError: If status doesn't match expected
        """
        if not resp or not hasattr(resp, 'status'):
            raise gl.vm.UserError(f"{name}: invalid response")
        if resp.status != expected_status:
            raise gl.vm.UserError(f"{name}: http {resp.status}")
    
    def get(self, url: str, headers: dict = None, expected_status: int = 200) -> any:
        """
        Make GET request with error handling.
        
        Args:
            url: Target URL
            headers: Optional headers dict
            expected_status: Expected HTTP status (default: 200)
            
        Returns:
            Response object
            
        Raises:
            gl.vm.UserError: If request fails or status doesn't match
        """
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
        """
        Convert value to float with error handling.
        
        Args:
            name: Name for error messages
            val: Value to convert
            
        Returns:
            Float value
            
        Raises:
            gl.vm.UserError: If conversion fails
        """
        try:
            return float(val)
        except Exception:
            raise gl.vm.UserError(f"{name}: parse float error")
    
    def to_int(self, name: str, val) -> int:
        """
        Convert value to int with error handling.
        
        Args:
            name: Name for error messages
            val: Value to convert
            
        Returns:
            Integer value
            
        Raises:
            gl.vm.UserError: If conversion fails
        """
        try:
            return int(val)
        except Exception:
            raise gl.vm.UserError(f"{name}: parse int error")


class PriceFeedPattern:
    """
    Pre-built pattern for cryptocurrency price feeds.
    
    Supports multiple Binance mirrors with Coingecko fallback.
    """
    
    def __init__(self):
        self.fetcher = WebFetcher()
    
    def get_price(self, symbol: str, binance_hosts: list = None, coingecko_fallback: bool = True) -> dict:
        """
        Get cryptocurrency price with multi-source fallback.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "ETH", "BTC")
            binance_hosts: List of Binance API hosts to try
            coingecko_fallback: Whether to use Coingecko as fallback
            
        Returns:
            Dict with "price" (float) and "source" (str)
            
        Raises:
            gl.vm.UserError: If all sources fail
        """
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


class WeatherPattern:
    """
    Pre-built pattern for weather data from Open-Meteo API.
    """
    
    def __init__(self):
        self.fetcher = WebFetcher()
    
    def get_weather(self, lat: float, lon: float, name: str = "weather") -> dict:
        """
        Get weather data from Open-Meteo.
        
        Args:
            lat: Latitude
            lon: Longitude
            name: Name for error messages
            
        Returns:
            Dict with "temperature" (float) and "condition" (str)
            
        Raises:
            gl.vm.UserError: If request fails
        """
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            resp = self.fetcher.get(url)
            data = self.fetcher.json(resp, name)
            
            current = data.get("current_weather") or {}
            temperature = self.fetcher.to_float(
                f"{name} temperature",
                current.get("temperature", 0.0)
            )
            condition = str(current.get("weathercode", "Unknown"))
            
            return {
                "temperature": temperature,
                "condition": condition
            }
        except gl.vm.UserError:
            raise
        except Exception as e:
            raise gl.vm.UserError(f"{name} error: {str(e)}")


class NewsPattern:
    """
    Pre-built pattern for fetching news from multiple sources.
    """
    
    def __init__(self):
        self.fetcher = WebFetcher()
    
    def get_news(self, source_urls: list, limit: int = 10) -> list:
        """
        Get news items from multiple sources with fallback.
        
        Args:
            source_urls: List of source URLs to try (in order)
            limit: Maximum number of items to return
            
        Returns:
            List of news items
        """
        news_items = []
        
        for url in source_urls:
            try:
                resp = self.fetcher.get(url)
                # Parse based on content type (JSON or RSS)
                # This is a simplified version - extend as needed
                if "json" in url.lower() or "reddit" in url.lower():
                    data = self.fetcher.json(resp, url)
                    # Reddit format
                    if "data" in data:
                        posts = data.get("data", {}).get("children", [])
                        for post in posts[:limit]:
                            news_items.append({
                                "title": post.get("data", {}).get("title", ""),
                                "source": "reddit"
                            })
                else:
                    # RSS format - simplified parsing
                    text = self.fetcher.text(resp, url)
                    # Count items as proxy
                    item_count = min(text.count("<item>"), limit)
                    for i in range(item_count):
                        news_items.append({
                            "title": f"News item {i+1}",
                            "source": url
                        })
                
                if news_items:
                    break  # Got data, stop trying other sources
            except Exception:
                continue  # Try next source
        
        return news_items[:limit]

