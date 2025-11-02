# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
Oracle Contract with Encrypted On-chain API Key

API key is encrypted and stored on-chain.
Only leader can decrypt it during execution.

Architecture:
  Contract (encrypted key) → Leader decrypts → External API → Result

Benefits:
  - On-chain storage: Keys are part of contract state (auditable)
  - No external dependency: No proxy service needed
  - Verifiable: Contract logic is verifiable

Trade-offs:
  - Key exposure risk: If leader is compromised, key is exposed
  - Key rotation complexity: Requires contract update
  - Encryption overhead: Encrypt/decrypt operations

Security Note:
  This example uses base64 encoding for simplicity.
  In production, use proper encryption (AES-256, Fernet, etc.)
  and store decryption keys securely on leader nodes.
"""
import json
import base64
import genlayer.gl as gl


class EncryptedKeyOracle(gl.Contract):
    """
    Oracle with encrypted API key stored on-chain.
    
    The API key is encrypted and stored as contract state.
    Only the leader node can decrypt it during execution.
    Validators verify results without seeing the decrypted key.
    """
    
    # Persistent state
    last_price: float
    last_source: str
    encrypted_api_key: str  # Base64-encoded encrypted key
    
    def __init__(self):
        # Initialize state
        self.last_price = 0.0
        self.last_source = ""
        # Encrypted API key (set via set_api_key method after deployment)
        self.encrypted_api_key = ""
    
    @gl.public.write
    def set_api_key(self, encrypted_key: str) -> None:
        """
        Set encrypted API key.
        
        This should be called once after deployment.
        Only contract owner should call this.
        
        Args:
            encrypted_key: Base64-encoded encrypted API key
                          (Encrypt off-chain before calling)
        
        Security Note:
          In production, use proper encryption:
          - Encrypt API key off-chain using AES-256 or Fernet
          - Base64 encode the encrypted result
          - Store decryption key securely on leader nodes only
        """
        if not encrypted_key or encrypted_key == "":
            raise gl.vm.UserError("encrypted key cannot be empty")
        
        # Store encrypted key
        self.encrypted_api_key = str(encrypted_key)
        _ = self.encrypted_api_key  # Force persistence
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price."""
        return {
            "price": str(self.last_price),
            "source": self.last_source,
            "has_api_key": bool(self.encrypted_api_key and self.encrypted_api_key != "")
        }
    
    @gl.public.write
    def update_price(self, symbol: str = "ETH") -> None:
        """
        Fetch price using encrypted on-chain API key.
        
        Leader decrypts key, makes API call, validators verify result.
        
        Args:
            symbol: Cryptocurrency symbol (default: "ETH")
        """
        # Check if API key is set
        if not self.encrypted_api_key or self.encrypted_api_key == "":
            raise gl.vm.UserError("api key not set. call set_api_key first")
        
        def leader():
            """Leader decrypts key and makes API call."""
            try:
                # Decrypt API key
                # WARNING: This is a simplified example using base64
                # In production, use proper encryption (AES-256, Fernet, etc.)
                # and store decryption keys securely on leader nodes
                
                # Decode base64-encoded encrypted key
                encrypted_bytes = base64.b64decode(self.encrypted_api_key.encode())
                
                # In production: decrypt using proper encryption library
                # For this example: assume base64 encoding is the "encryption"
                # (NOT SECURE - this is just for demonstration)
                api_key = encrypted_bytes.decode("utf-8")
                
            except Exception as e:
                raise gl.vm.UserError(f"api key decrypt error: {str(e)}")
            
            if not api_key or api_key == "":
                raise gl.vm.UserError("decrypted api key is empty")
            
            # Make API call with decrypted key
            # Example: Coingecko Pro API
            try:
                coingecko_url = (
                    f"https://api.coingecko.com/api/v3/simple/price"
                    f"?ids={symbol.lower()}&vs_currencies=usd"
                )
                
                response = gl.nondet.web.get(
                    coingecko_url,
                    headers={
                        "User-Agent": "GenLayerOracle/1.0",
                        "X-CG-Pro-API-Key": api_key  # Decrypted key used here
                    }
                )
            except Exception as e:
                raise gl.vm.UserError(f"api request failed: {str(e)}")
            
            # Validate response
            if not response or not hasattr(response, 'status'):
                raise gl.vm.UserError("api request failed: no response")
            
            if response.status != 200:
                error_body = ""
                if response.body:
                    try:
                        error_body = response.body.decode("utf-8")[:100]
                    except:
                        pass
                raise gl.vm.UserError(
                    f"api error {response.status}: {error_body}"
                )
            
            # Parse response
            if not response.body:
                raise gl.vm.UserError("api response empty")
            
            try:
                body_text = response.body.decode("utf-8")
                data = json.loads(body_text)
            except Exception as e:
                raise gl.vm.UserError(f"api response parse error: {str(e)}")
            
            # Extract price
            price_data = data.get(symbol.lower())
            if not price_data or not isinstance(price_data, dict):
                raise gl.vm.UserError(f"price data missing for {symbol}")
            
            price = price_data.get("usd")
            if price is None:
                raise gl.vm.UserError(f"usd price not found for {symbol}")
            
            try:
                price_float = float(price)
                if price_float <= 0:
                    raise gl.vm.UserError(f"invalid price: {price_float}")
            except (ValueError, TypeError) as e:
                raise gl.vm.UserError(f"price parse error: {str(e)}")
            
            return {
                "price": str(price_float),
                "source": "coingecko-pro",
                "symbol": symbol.upper()
            }
        
        def validator(result):
            """Validators verify result (never see API key)."""
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
        source_str = data.get("source", "coingecko-pro")
        
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

