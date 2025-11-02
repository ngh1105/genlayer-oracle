# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
GenLayer Decentralized Oracle Contract

This contract fetches real-world data (crypto prices, weather, news) using
non-deterministic execution with leader-validator consensus. All data is
persisted on-chain and can be queried by any dApp.

Data Sources:
- Price: Binance (6 mirrors) + Coingecko fallback
- Weather: Open-Meteo API
- News: Reddit + CoinDesk RSS fallback
"""
import json
import genlayer.gl as gl


# Event removed - not needed for persistence and causes deployment errors
# If events are needed in the future, they must be defined with proper GenLayer Event syntax

class OracleConsumer(gl.Contract):
    """
    Decentralized Oracle Contract for fetching and storing real-world data.
    
    Uses GenLayer's non-deterministic execution with validator consensus to
    ensure data integrity while allowing access to external APIs.
    """
    
    # CRITICAL: All persistent fields MUST be declared in class body with type annotations
    # Fields declared only in __init__ are NOT persistent and will be discarded!
    # Note: Use bigint or sized integers (u256, i32, etc.) - plain 'int' is not allowed!
    # Using str for news_count to avoid bigint import (convert to int when reading)
    last_eth_price: float
    last_eth_source: str
    last_weather_temperature: float
    last_weather_condition: str
    last_weather_city: str
    last_news_count: str  # Store as string (news count is small, string is safe)
    
    def __init__(self):
        # Initialize state variables with defaults
        self.last_eth_price = 0.0
        self.last_eth_source = ""
        # Store weather fields separately for proper persistence
        self.last_weather_temperature = 0.0
        self.last_weather_condition = ""
        self.last_weather_city = ""
        self.last_news_count = "0"  # Initialize as string

    @gl.public.view
    def debug_state(self) -> dict:
        """Debug method to check if state is persisted"""
        return {
            "has_price": hasattr(self, 'last_eth_price'),
            "price_value": str(getattr(self, 'last_eth_price', 'NOT_SET')),
            "has_source": hasattr(self, 'last_eth_source'),
            "source_value": getattr(self, 'last_eth_source', 'NOT_SET'),
            "has_temp": hasattr(self, 'last_weather_temperature'),
            "temp_value": str(getattr(self, 'last_weather_temperature', 'NOT_SET')),
            "contract_address": str(self.address) if hasattr(self, 'address') else 'NO_ADDRESS',
        }
    
    @gl.public.view
    def get_status(self) -> dict:
        # Safe initialization if attributes don't exist (shouldn't happen if __init__ ran)
        if not hasattr(self, 'last_eth_price'):
            self.last_eth_price = 0.0
        if not hasattr(self, 'last_eth_source'):
            self.last_eth_source = ""
        if not hasattr(self, 'last_weather_temperature'):
            self.last_weather_temperature = 0.0
        if not hasattr(self, 'last_weather_condition'):
            self.last_weather_condition = ""
        if not hasattr(self, 'last_weather_city'):
            self.last_weather_city = ""
        if not hasattr(self, 'last_news_count'):
            self.last_news_count = "0"
        
        # Convert floats to strings for calldata encoding
        return {
            "price": {
                "eth_usd": str(self.last_eth_price),
                "source": self.last_eth_source,
            },
            "weather": {
                "temperature": str(self.last_weather_temperature),
                "condition": self.last_weather_condition,
                "city": self.last_weather_city,
            },
            "news": {"count": int(self.last_news_count)},  # Convert string to int for return
        }

    @gl.public.write
    def update_all(self, city: str = "Hanoi", lat: str = "21.0245", lon: str = "105.8412", news_limit: int = 3) -> None:
        # parse coordinates from strings to floats inside the method
        try:
            _lat = float(lat)
            _lon = float(lon)
        except Exception:
            raise gl.vm.UserError(f"invalid coordinates: lat={lat}, lon={lon}")
        
        def leader():
            def _ensure_body_bytes(resp, name: str):
                if resp.body is None:
                    raise gl.vm.UserError(f"{name} empty body")
                try:
                    return resp.body.decode("utf-8")
                except Exception:
                    raise gl.vm.UserError(f"{name} body decode error")

            def _json(resp, name: str):
                text = _ensure_body_bytes(resp, name)
                try:
                    return json.loads(text)
                except Exception:
                    raise gl.vm.UserError(f"{name} json parse error")

            def _to_float(name: str, val):
                try:
                    return float(val)
                except Exception:
                    raise gl.vm.UserError(f"{name} parse float error")
            
            try:
                # Price from multiple sources with fallback
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
                
                # Try Binance mirrors first
                for host in binance_hosts:
                    try:
                        resp = gl.nondet.web.get(
                            f"{host}/api/v3/ticker/price?symbol=ETHUSDT",
                            headers={"User-Agent": "GenLayerOracle/1.0"},
                        )
                        if resp and hasattr(resp, 'status') and resp.status == 200:
                            data = _json(resp, f"binance-{host}")
                            price_str = (data.get("price") if isinstance(data, dict) else None)
                            if price_str is not None:
                                price = _to_float("binance price", price_str)
                                price_source = "binance"
                                break
                    except gl.vm.UserError:
                        continue  # try next mirror on UserError
                    except Exception:
                        continue  # try next mirror on any other error
                
                # Fallback to Coingecko if all Binance mirrors fail
                if price is None:
                    try:
                        coingecko = gl.nondet.web.get(
                            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                            headers={"User-Agent": "GenLayerOracle/1.0"},
                        )
                        if coingecko and hasattr(coingecko, 'status') and coingecko.status == 200:
                            data = _json(coingecko, "coingecko")
                            eth_data = data.get("ethereum") if isinstance(data, dict) else None
                            if eth_data and isinstance(eth_data, dict):
                                usd_val = eth_data.get("usd")
                                if usd_val is not None:
                                    price = _to_float("coingecko price", usd_val)
                                    price_source = "coingecko"
                    except Exception:
                        pass  # fallback silently
                
                if price is None or price <= 0 or price_source is None:
                    raise gl.vm.UserError("all price sources failed")

                # Weather from Open-Meteo
                try:
                    meteo = gl.nondet.web.get(
                        f"https://api.open-meteo.com/v1/forecast?latitude={_lat}&longitude={_lon}&current_weather=true",
                        headers={"User-Agent": "GenLayerOracle/1.0"},
                    )
                    if not meteo or not hasattr(meteo, 'status') or meteo.status != 200:
                        raise gl.vm.UserError(f"open-meteo http {getattr(meteo, 'status', 'unknown')}")
                    meteo_json = _json(meteo, "open-meteo")
                    cw = meteo_json.get("current_weather") or {}
                    temperature = _to_float("open-meteo temperature", cw.get("temperature", 0.0))
                    condition = str(cw.get("weathercode", "Unknown"))
                except gl.vm.UserError:
                    raise  # Re-raise UserError
                except Exception as e:
                    raise gl.vm.UserError(f"open-meteo error: {str(e)}")

                # Crypto news from Reddit (with fallback handling)
                news_count = 0
                reddit_ok = False
                
                try:
                    reddit = gl.nondet.web.get(
                        f"https://www.reddit.com/r/CryptoCurrency/hot.json?limit={news_limit}&raw_json=1",
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 GenLayerOracle/1.0"
                            )
                        },
                    )
                    if reddit and hasattr(reddit, 'status'):
                        if reddit.status == 200:
                            reddit_json = _json(reddit, "reddit")
                            posts = (reddit_json.get("data", {}) or {}).get("children", [])
                            if isinstance(posts, list):
                                news_count = int(len(posts))
                                reddit_ok = True
                        elif reddit.status == 403:
                            # Rate limited or geo-restricted; fallback to zero silently
                            news_count = 0
                            reddit_ok = True
                except Exception:
                    # Any error: fallback to zero instead of rollback
                    news_count = 0
                    reddit_ok = True
                
                # If Reddit completely failed, try RSS fallback (CoinDesk RSS)
                if not reddit_ok:
                    try:
                        rss = gl.nondet.web.get(
                            "https://www.coindesk.com/arc/outboundfeeds/rss/",
                            headers={"User-Agent": "GenLayerOracle/1.0"},
                        )
                        if rss and hasattr(rss, 'status') and rss.status == 200 and hasattr(rss, 'body') and rss.body:
                            # Simple RSS item count (approximate)
                            rss_text = rss.body.decode("utf-8", errors="ignore")
                            # Count <item> tags as proxy for news items
                            news_count = min(int(rss_text.count("<item>")), news_limit)
                    except Exception:
                        pass  # final fallback: keep news_count = 0

                return {
                    "price": {"value": str(price), "source": price_source},
                    "weather": {"temperature": str(temperature), "condition": condition, "city": city},
                    "news": {"count": news_count},
                }
            except gl.vm.UserError:
                raise  # Re-raise UserError
            except gl.vm.VMError as e:
                raise gl.vm.UserError(f"VM error in leader: {str(e)}")
            except Exception as e:
                raise gl.vm.UserError(f"leader error: {str(e)}")

        def validator(result):
            # result is gl.vm.Return on success; unpack and verify
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                
                # Safe dict access with .get()
                price_obj = unpacked.get("price")
                if not isinstance(price_obj, dict):
                    return False
                p_val = price_obj.get("value")
                try:
                    p = float(p_val)
                    if p <= 0:
                        return False
                except Exception:
                    return False
                
                weather_obj = unpacked.get("weather")
                if not isinstance(weather_obj, dict):
                    return False
                try:
                    _ = float(weather_obj.get("temperature", 0))
                    _ = str(weather_obj.get("condition", ""))
                except Exception:
                    return False
                
                news_obj = unpacked.get("news")
                if not isinstance(news_obj, dict):
                    return False
                try:
                    n = int(news_obj.get("count", 0))
                    if n < 0:
                        return False
                except Exception:
                    return False
                
                return True
            except Exception:
                return False

        try:
            try:
                data = gl.vm.run_nondet(leader, validator)
            except gl.vm.UserError:
                raise  # Re-raise UserError
            except gl.vm.VMError as e:
                raise gl.vm.UserError(f"VM error in run_nondet: {str(e)}")
            except Exception as e:
                raise gl.vm.UserError(f"run_nondet error: {str(e)}")
            
            # Safe unpacking and assignment
            if not isinstance(data, dict):
                raise gl.vm.UserError("invalid result format")
            
            price_obj = data.get("price") or {}
            if not isinstance(price_obj, dict):
                raise gl.vm.UserError("invalid price format")
            
            weather_obj = data.get("weather") or {}
            if not isinstance(weather_obj, dict):
                raise gl.vm.UserError("invalid weather format")
            
            news_obj = data.get("news") or {}
            if not isinstance(news_obj, dict):
                raise gl.vm.UserError("invalid news format")
            
            # Parse and assign with safe defaults
            # Note: values come as strings from leader() return
            price_val = price_obj.get("value")
            if price_val is None:
                raise gl.vm.UserError("missing price value")
            # Parse string to float and assign - ensure persistence
            try:
                price_float = float(str(price_val))
                self.last_eth_price = price_float
                # Force storage write by reassigning
                _ = self.last_eth_price
            except (ValueError, TypeError):
                raise gl.vm.UserError(f"invalid price value: {price_val}")
            
            source_str = str(price_obj.get("source", "unknown"))
            self.last_eth_source = source_str
            _ = self.last_eth_source
            
            temp_val = weather_obj.get("temperature")
            if temp_val is None:
                raise gl.vm.UserError("missing temperature")
            # Parse string to float
            try:
                temp_float = float(str(temp_val))
                self.last_weather_temperature = temp_float
                _ = self.last_weather_temperature
            except (ValueError, TypeError):
                raise gl.vm.UserError(f"invalid temperature value: {temp_val}")
            
            self.last_weather_condition = str(weather_obj.get("condition", "Unknown"))
            _ = self.last_weather_condition
            
            self.last_weather_city = str(weather_obj.get("city", city))
            _ = self.last_weather_city
            
            news_count_val = news_obj.get("count")
            if news_count_val is None:
                raise gl.vm.UserError("missing news count")
            try:
                news_int = int(news_count_val)
                # Store as string to avoid bigint type issues
                self.last_news_count = str(news_int)
                _ = self.last_news_count
            except (ValueError, TypeError):
                raise gl.vm.UserError(f"invalid news count: {news_count_val}")
            
            # Event emission removed - not needed for state persistence
            # State is persisted via field assignments above
            
        except gl.vm.UserError:
            raise  # Re-raise UserError as-is
        except Exception as e:
            raise gl.vm.UserError(f"update_all failed: {str(e)}") 



