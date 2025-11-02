# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
Oracle Contract with Key Rotation Support

Supports multiple API keys with automatic rotation.
Contract can switch between keys without downtime.

Architecture:
  Contract (keys: [key1, key2, key3])
    → Leader tries key1 → if fails → try key2 → etc.
    → Update active key based on success

Benefits:
  - Zero downtime rotation: Switch keys without contract downtime
  - Fallback support: Multiple keys for redundancy
  - Key health monitoring: Track which keys work
  - Flexible management: Add/remove keys dynamically

Trade-offs:
  - On-chain storage cost: Storing multiple keys uses more storage
  - Complexity: More complex contract logic
  - Key management: Need to manage multiple keys
"""
import json
import base64
import genlayer.gl as gl


class RotatingKeyOracle(gl.Contract):
    """
    Oracle with support for multiple API keys and rotation.
    
    The contract maintains a list of encrypted API keys.
    On failure, it automatically tries the next key.
    The active key index is updated based on success.
    """
    
    # Persistent state
    last_price: float
    last_source: str
    api_keys: list  # List of encrypted API keys (base64 strings)
    active_key_index: int  # Index of currently active key
    key_success_count: dict  # Track success count per key (for monitoring)
    
    def __init__(self):
        # Initialize state
        self.last_price = 0.0
        self.last_source = ""
        self.api_keys = []  # Will store encrypted keys (as strings)
        self.active_key_index = 0
        self.key_success_count = {}  # key_index (as string) -> success_count (as string)
    
    @gl.public.write
    def add_api_key(self, encrypted_key: str) -> None:
        """
        Add a new API key to the rotation pool.
        
        Args:
            encrypted_key: Base64-encoded encrypted API key
        
        Note:
          Keys should be encrypted off-chain before adding.
          See scripts/encrypt_key.py for encryption example.
        """
        if not encrypted_key or encrypted_key == "":
            raise gl.vm.UserError("encrypted key cannot be empty")
        
        # Add key to list
        self.api_keys.append(str(encrypted_key))
        
        # Initialize success count for new key
        key_index = len(self.api_keys) - 1
        key_index_str = str(key_index)
        self.key_success_count[key_index_str] = "0"
        
        # Force persistence
        _ = self.api_keys
        _ = self.key_success_count
    
    @gl.public.write
    def rotate_key(self) -> None:
        """
        Manually rotate to next key in the pool.
        
        Useful for manual key rotation or testing.
        Automatic rotation happens on failure.
        """
        if len(self.api_keys) == 0:
            raise gl.vm.UserError("no keys available")
        
        # Rotate to next key (circular)
        self.active_key_index = (self.active_key_index + 1) % len(self.api_keys)
        _ = self.active_key_index
    
    @gl.public.view
    def get_key_status(self) -> dict:
        """
        Get status of all keys (for monitoring).
        
        Returns:
            Dictionary with key count, active index, and success counts
        """
        return {
            "key_count": len(self.api_keys),
            "active_key_index": self.active_key_index,
            "success_counts": dict(self.key_success_count),
            "last_price": str(self.last_price),
            "last_source": self.last_source
        }
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price."""
        return {
            "price": str(self.last_price),
            "source": self.last_source,
            "active_key_index": self.active_key_index,
            "key_count": len(self.api_keys)
        }
    
    @gl.public.write
    def update_price(self, symbol: str = "ETH") -> None:
        """
        Fetch price using active API key, rotate on failure.
        
        The contract tries keys in order:
        1. Starts with active key
        2. On failure, tries next key
        3. Updates active key to successful key
        
        Args:
            symbol: Cryptocurrency symbol (default: "ETH")
        """
        if len(self.api_keys) == 0:
            raise gl.vm.UserError("no api keys configured. call add_api_key first")
        
        def leader():
            """Leader tries keys in order, rotates on failure."""
            keys_to_try = len(self.api_keys)
            last_error = None
            
            # Try active key first, then others in circular order
            for attempt in range(keys_to_try):
                key_index = (self.active_key_index + attempt) % len(self.api_keys)
                encrypted_key = self.api_keys[key_index]
                
                try:
                    # Decrypt key (simplified - use proper encryption in production)
                    try:
                        encrypted_bytes = base64.b64decode(encrypted_key.encode())
                        api_key = encrypted_bytes.decode("utf-8")
                    except Exception as e:
                        last_error = f"key {key_index} decrypt error: {str(e)}"
                        continue  # Try next key
                    
                    if not api_key or api_key == "":
                        last_error = f"key {key_index} empty after decrypt"
                        continue
                    
                    # Make API call
                    try:
                        response = gl.nondet.web.get(
                            f"https://api.coingecko.com/api/v3/simple/price"
                            f"?ids={symbol.lower()}&vs_currencies=usd",
                            headers={
                                "User-Agent": "GenLayerOracle/1.0",
                                "X-CG-Pro-API-Key": api_key  # Decrypted key
                            }
                        )
                    except Exception as e:
                        last_error = f"key {key_index} request error: {str(e)}"
                        continue  # Try next key
                    
                    # Check response
                    if not response or not hasattr(response, 'status'):
                        last_error = f"key {key_index} no response"
                        continue
                    
                    if response.status != 200:
                        last_error = f"key {key_index} status {response.status}"
                        continue  # Try next key
                    
                    # Parse response
                    if not response.body:
                        last_error = f"key {key_index} empty body"
                        continue
                    
                    try:
                        body_text = response.body.decode("utf-8")
                        data = json.loads(body_text)
                    except Exception as e:
                        last_error = f"key {key_index} parse error: {str(e)}"
                        continue
                    
                    # Extract price
                    price_data = data.get(symbol.lower())
                    if not price_data or not isinstance(price_data, dict):
                        last_error = f"key {key_index} price data missing"
                        continue
                    
                    price = price_data.get("usd")
                    if price is None:
                        last_error = f"key {key_index} usd price missing"
                        continue
                    
                    try:
                        price_float = float(price)
                        if price_float <= 0:
                            last_error = f"key {key_index} invalid price: {price_float}"
                            continue
                    except (ValueError, TypeError):
                        last_error = f"key {key_index} price parse error"
                        continue
                    
                    # SUCCESS - this key worked
                    # Update success count for this key
                    key_index_str = str(key_index)
                    current_count_str = self.key_success_count.get(key_index_str, "0")
                    try:
                        current_count = int(current_count_str)
                        new_count = current_count + 1
                    except:
                        new_count = 1
                    
                    self.key_success_count[key_index_str] = str(new_count)
                    
                    # Switch to this key if it's not the active one
                    if key_index != self.active_key_index:
                        self.active_key_index = key_index
                        _ = self.active_key_index
                    
                    return {
                        "price": str(price_float),
                        "source": f"coingecko-key-{key_index}",
                        "key_index": key_index,
                        "symbol": symbol.upper()
                    }
                    
                except Exception as e:
                    last_error = f"key {key_index} error: {str(e)}"
                    continue  # Try next key
            
            # All keys failed
            raise gl.vm.UserError(
                f"all {keys_to_try} keys failed. last error: {last_error}"
            )
        
        def validator(result):
            """Validators verify result (never see API keys)."""
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
        source_str = data.get("source", "unknown")
        
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

