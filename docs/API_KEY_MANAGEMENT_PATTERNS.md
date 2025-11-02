# API Key Management Patterns for GenLayer Contracts

## 🎯 Problem Statement

**Challenge**: Intelligent Contracts often need to interact with APIs that require authentication keys. However, we must balance:
- **Security**: Keep API keys private and secure
- **Verifiability**: Contracts must remain verifiable and trustless
- **Flexibility**: Support key rotation and multiple keys

## 🔐 Pattern Overview

This document describes three main patterns for handling API keys in GenLayer contracts:

1. **Off-chain Proxy Pattern** - Keys never touch the blockchain
2. **Encrypted On-chain Pattern** - Encrypted keys stored on-chain
3. **Key Rotation Pattern** - Support for rotating keys without downtime

---

## Pattern 1: Off-chain Proxy Pattern

### Concept

Contract calls an off-chain proxy service that holds API keys. Keys never appear on-chain.

```
Contract → Proxy Service (holds keys) → External API → Proxy → Contract
```

### Architecture

- **Contract**: Makes HTTP requests to proxy service
- **Proxy Service**: Runs off-chain, holds API keys, acts as gateway
- **External API**: Protected by API key (invisible to contract)

### Advantages

✅ **Maximum Security**: Keys never exposed on-chain
✅ **Key Privacy**: Complete separation of keys from contract
✅ **Easy Rotation**: Update keys in proxy without contract changes
✅ **Rate Limit Control**: Proxy can manage rate limits centrally

### Disadvantages

❌ **Centralization**: Requires trusted proxy service
❌ **Single Point of Failure**: Proxy must be reliable
❌ **Cost**: Running proxy service infrastructure

### Implementation Example

#### Contract (Python)

```python
# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
Oracle Contract using Off-chain Proxy Pattern

The contract calls a proxy service that holds API keys.
Keys never appear in contract code or on-chain.
"""
import genlayer.gl as gl


class ProxyOracle(gl.Contract):
    """
    Oracle that uses off-chain proxy for API key management.
    """
    
    # Persistent state
    last_price: float
    last_source: str
    proxy_url: str  # Proxy service URL
    
    def __init__(self):
        self.last_price = 0.0
        self.last_source = ""
        # Proxy service URL (configured at deployment)
        self.proxy_url = "https://your-proxy-service.com/api"
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price."""
        return {
            "price": str(self.last_price),
            "source": self.last_source
        }
    
    @gl.public.write
    def update_price(self, symbol: str = "ETH") -> None:
        """
        Fetch price via proxy service.
        Proxy service handles API key authentication.
        """
        def leader():
            """Leader fetches data via proxy (proxy has API keys)."""
            # Call proxy service (proxy adds API key headers)
            proxy_response = gl.nondet.web.get(
                f"{self.proxy_url}/price/{symbol}",
                headers={
                    "User-Agent": "GenLayerOracle/1.0",
                    # NO API KEY HERE - Proxy handles it
                }
            )
            
            if not proxy_response or not hasattr(proxy_response, 'status'):
                raise gl.vm.UserError("proxy service unavailable")
            
            if proxy_response.status != 200:
                raise gl.vm.UserError(f"proxy error: {proxy_response.status}")
            
            # Parse response
            import json
            body = proxy_response.body.decode("utf-8") if proxy_response.body else "{}"
            data = json.loads(body)
            
            price_str = data.get("price")
            source = data.get("source", "proxy")
            
            if price_str is None:
                raise gl.vm.UserError("invalid proxy response")
            
            try:
                price = float(price_str)
            except:
                raise gl.vm.UserError("price parse error")
            
            return {"price": str(price), "source": source}
        
        def validator(result):
            """Validate proxy response."""
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                price_str = unpacked.get("price")
                if price_str:
                    price = float(price_str)
                    return price > 0 and price < 100000
                return False
            except Exception:
                return False
        
        # Run consensus
        try:
            data = gl.vm.run_nondet(leader, validator)
        except gl.vm.UserError:
            raise
        except Exception as e:
            raise gl.vm.UserError(f"update_price failed: {str(e)}")
        
        # Update state
        if not isinstance(data, dict):
            raise gl.vm.UserError("invalid result format")
        
        price_str = data.get("price")
        source_str = data.get("source", "proxy")
        
        try:
            self.last_price = float(price_str)
            _ = self.last_price  # Force persistence
        except:
            raise gl.vm.UserError("price assignment error")
        
        self.last_source = source_str
        _ = self.last_source
```

#### Proxy Service (Node.js Example)

```javascript
// proxy-service/server.js
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

// API keys stored in environment variables (never in code)
const COINGECKO_API_KEY = process.env.COINGECKO_API_KEY;
const BINANCE_API_KEY = process.env.BINANCE_API_KEY;

// Proxy endpoint for price
app.get('/api/price/:symbol', async (req, res) => {
  const symbol = req.params.symbol;
  
  try {
    // Proxy adds API key (contract doesn't see it)
    const response = await axios.get(
      'https://api.coingecko.com/api/v3/simple/price',
      {
        params: { ids: symbol.toLowerCase(), vs_currencies: 'usd' },
        headers: {
          'X-CG-Pro-API-Key': COINGECKO_API_KEY  // API key added here
        }
      }
    );
    
    const price = response.data[symbol.toLowerCase()]?.usd;
    
    if (!price) {
      return res.status(404).json({ error: 'Price not found' });
    }
    
    // Return formatted response
    res.json({
      price: price.toString(),
      source: 'coingecko-proxy',
      timestamp: Date.now()
    });
  } catch (error) {
    res.status(500).json({ error: 'Proxy error', message: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Proxy service running on port ${PORT}`);
});
```

### Deployment Guide

1. **Deploy Proxy Service**:
   ```bash
   # Set API keys in environment
   export COINGECKO_API_KEY=your_key_here
   export BINANCE_API_KEY=your_key_here
   
   # Run proxy service
   node proxy-service/server.js
   ```

2. **Update Contract**:
   ```python
   # Set proxy URL in contract __init__
   self.proxy_url = "https://your-proxy-service.com/api"
   ```

3. **Deploy Contract**: Use GenLayer Studio

### Security Considerations

- ✅ Use HTTPS for proxy service
- ✅ Implement rate limiting in proxy
- ✅ Use environment variables for keys (never hardcode)
- ✅ Monitor proxy service logs
- ✅ Consider IP whitelisting for proxy endpoints
- ⚠️ Proxy service is a trusted component (centralization risk)

---

## Pattern 2: Encrypted On-chain Pattern

### Concept

API keys are encrypted and stored on-chain. Only the leader node can decrypt during execution.

```
Contract (encrypted key) → Leader decrypts → External API → Result
```

### Architecture

- **Contract Storage**: Encrypted API key stored as contract state
- **Leader Decryption**: Leader node decrypts key (using its private key)
- **External API**: Called with decrypted key
- **Validators**: Verify result (never see decrypted key)

### Advantages

✅ **On-chain Storage**: Keys are part of contract state (auditable)
✅ **Leader-only Decryption**: Only leader sees decrypted key
✅ **No External Dependency**: No proxy service needed
✅ **Verifiable**: Contract logic is verifiable

### Disadvantages

❌ **Key Exposure Risk**: If leader is compromised, key is exposed
❌ **Key Rotation Complexity**: Requires contract update
❌ **Encryption Overhead**: Encrypt/decrypt operations

### Implementation Example

```python
# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
Oracle Contract with Encrypted On-chain API Key

API key is encrypted and stored on-chain.
Only leader can decrypt it during execution.
"""
import genlayer.gl as gl
import base64
import hashlib


class EncryptedKeyOracle(gl.Contract):
    """
    Oracle with encrypted API key stored on-chain.
    """
    
    # Persistent state
    last_price: float
    last_source: str
    encrypted_api_key: str  # Base64-encoded encrypted key
    
    def __init__(self):
        self.last_price = 0.0
        self.last_source = ""
        # Encrypted API key (set via set_api_key method)
        self.encrypted_api_key = ""
    
    @gl.public.write
    def set_api_key(self, encrypted_key: str) -> None:
        """
        Set encrypted API key.
        
        This should be called once after deployment.
        Only contract owner should call this.
        """
        # Store encrypted key (plain storage, encryption assumed done off-chain)
        self.encrypted_api_key = encrypted_key
        _ = self.encrypted_api_key
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price."""
        return {
            "price": str(self.last_price),
            "source": self.last_source
        }
    
    @gl.public.write
    def update_price(self, symbol: str = "ETH") -> None:
        """
        Fetch price using encrypted on-chain API key.
        
        Leader decrypts key, makes API call, validators verify result.
        """
        def leader():
            """Leader decrypts key and makes API call."""
            # Decrypt API key (leader-only operation)
            # In practice, use proper encryption (AES, etc.)
            # For demo: assume simple base64 (NOT secure in production!)
            try:
                # Decode encrypted key (simplified - use proper encryption)
                # WARNING: This is a demo - use proper encryption library
                api_key = base64.b64decode(self.encrypted_api_key.encode()).decode()
            except Exception:
                raise gl.vm.UserError("api key decrypt error")
            
            if not api_key:
                raise gl.vm.UserError("api key not set")
            
            # Make API call with decrypted key
            # Example: Coingecko Pro API
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
            
            if not response or not hasattr(response, 'status'):
                raise gl.vm.UserError("api request failed")
            
            if response.status != 200:
                raise gl.vm.UserError(f"api error: {response.status}")
            
            # Parse response
            import json
            body = response.body.decode("utf-8") if response.body else "{}"
            data = json.loads(body)
            
            price_data = data.get(symbol.lower())
            if not price_data:
                raise gl.vm.UserError("price data missing")
            
            price = price_data.get("usd")
            if price is None:
                raise gl.vm.UserError("price not found")
            
            return {
                "price": str(float(price)),
                "source": "coingecko-pro"
            }
        
        def validator(result):
            """Validators verify result (never see API key)."""
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                price_str = unpacked.get("price")
                if price_str:
                    price = float(price_str)
                    return price > 0 and price < 100000
                return False
            except Exception:
                return False
        
        # Run consensus
        try:
            data = gl.vm.run_nondet(leader, validator)
        except gl.vm.UserError:
            raise
        except Exception as e:
            raise gl.vm.UserError(f"update_price failed: {str(e)}")
        
        # Update state
        if not isinstance(data, dict):
            raise gl.vm.UserError("invalid result format")
        
        price_str = data.get("price")
        source_str = data.get("source", "coingecko-pro")
        
        try:
            self.last_price = float(price_str)
            _ = self.last_price
        except:
            raise gl.vm.UserError("price assignment error")
        
        self.last_source = source_str
        _ = self.last_source
```

### Key Encryption (Off-chain Script)

```python
# scripts/encrypt_key.py
"""
Off-chain script to encrypt API key for on-chain storage.
"""
import base64
from cryptography.fernet import Fernet

# Generate encryption key (store securely, share with leader nodes)
key = Fernet.generate_key()
cipher = Fernet(key)

# API key to encrypt
api_key = "your-api-key-here"

# Encrypt
encrypted = cipher.encrypt(api_key.encode())
encrypted_b64 = base64.b64encode(encrypted).decode()

print(f"Encrypted key: {encrypted_b64}")
print(f"Decryption key (store securely): {key.decode()}")
```

### Security Considerations

- ✅ Use strong encryption (AES-256, Fernet)
- ✅ Store decryption key securely (leader nodes only)
- ✅ Rotate encryption keys periodically
- ✅ Limit API key permissions (use read-only keys when possible)
- ⚠️ Leader node compromise = API key exposure
- ⚠️ Ensure leader nodes are trusted and secure

---

## Pattern 3: Key Rotation Pattern

### Concept

Support multiple API keys with rotation capability. Contract can switch between keys without downtime.

```
Contract (keys: [key1, key2, key3])
  → Leader tries key1 → if fails → try key2 → etc.
  → Update active key based on success
```

### Architecture

- **Multiple Keys**: Contract stores array of API keys
- **Active Key Index**: Points to currently used key
- **Rotation Logic**: Automatically switch on failure
- **Key Status Tracking**: Monitor key usage and health

### Advantages

✅ **Zero Downtime Rotation**: Switch keys without contract downtime
✅ **Fallback Support**: Multiple keys for redundancy
✅ **Key Health Monitoring**: Track which keys work
✅ **Flexible Management**: Add/remove keys dynamically

### Disadvantages

❌ **On-chain Storage Cost**: Storing multiple keys uses more storage
❌ **Complexity**: More complex contract logic
❌ **Key Management**: Need to manage multiple keys

### Implementation Example

```python
# v0.1.0
# { "Depends": "py-genlayer:latest" }
"""
Oracle Contract with Key Rotation Support

Supports multiple API keys with automatic rotation.
"""
import genlayer.gl as gl


class RotatingKeyOracle(gl.Contract):
    """
    Oracle with support for multiple API keys and rotation.
    """
    
    # Persistent state
    last_price: float
    last_source: str
    api_keys: list  # List of encrypted API keys
    active_key_index: int  # Index of currently active key
    key_success_count: dict  # Track success per key
    
    def __init__(self):
        self.last_price = 0.0
        self.last_source = ""
        self.api_keys = []  # Will store encrypted keys
        self.active_key_index = 0
        self.key_success_count = {}  # key_index -> success_count
    
    @gl.public.write
    def add_api_key(self, encrypted_key: str) -> None:
        """
        Add a new API key to the rotation pool.
        """
        self.api_keys.append(encrypted_key)
        # Initialize success count
        key_index = len(self.api_keys) - 1
        self.key_success_count[str(key_index)] = 0
    
    @gl.public.write
    def rotate_key(self) -> None:
        """
        Manually rotate to next key.
        """
        if len(self.api_keys) == 0:
            raise gl.vm.UserError("no keys available")
        
        self.active_key_index = (self.active_key_index + 1) % len(self.api_keys)
        _ = self.active_key_index
    
    @gl.public.view
    def get_price(self) -> dict:
        """Get current stored price."""
        return {
            "price": str(self.last_price),
            "source": self.last_source,
            "active_key_index": self.active_key_index
        }
    
    @gl.public.write
    def update_price(self, symbol: str = "ETH") -> None:
        """
        Fetch price using active API key, rotate on failure.
        """
        if len(self.api_keys) == 0:
            raise gl.vm.UserError("no api keys configured")
        
        def leader():
            """Leader tries keys in order, rotates on failure."""
            keys_to_try = len(self.api_keys)
            last_error = None
            
            # Try active key first, then others
            for attempt in range(keys_to_try):
                key_index = (self.active_key_index + attempt) % len(self.api_keys)
                encrypted_key = self.api_keys[key_index]
                
                try:
                    # Decrypt key (simplified - use proper encryption)
                    import base64
                    api_key = base64.b64decode(encrypted_key.encode()).decode()
                    
                    # Make API call
                    response = gl.nondet.web.get(
                        f"https://api.coingecko.com/api/v3/simple/price"
                        f"?ids={symbol.lower()}&vs_currencies=usd",
                        headers={
                            "User-Agent": "GenLayerOracle/1.0",
                            "X-CG-Pro-API-Key": api_key
                        }
                    )
                    
                    if response and hasattr(response, 'status') and response.status == 200:
                        # Success - parse and return
                        import json
                        body = response.body.decode("utf-8") if response.body else "{}"
                        data = json.loads(body)
                        price_data = data.get(symbol.lower())
                        
                        if price_data and price_data.get("usd"):
                            price = float(price_data["usd"])
                            
                            # Update success count for this key
                            key_index_str = str(key_index)
                            current_count = self.key_success_count.get(key_index_str, 0)
                            self.key_success_count[key_index_str] = current_count + 1
                            
                            # Switch to this key if it's not the active one
                            if key_index != self.active_key_index:
                                self.active_key_index = key_index
                            
                            return {
                                "price": str(price),
                                "source": f"coingecko-key-{key_index}",
                                "key_index": key_index
                            }
                    
                    # This key failed, try next
                    last_error = f"key {key_index} failed: status {getattr(response, 'status', 'unknown')}"
                    
                except Exception as e:
                    last_error = f"key {key_index} error: {str(e)}"
                    continue  # Try next key
            
            # All keys failed
            raise gl.vm.UserError(f"all keys failed. last error: {last_error}")
        
        def validator(result):
            """Validators verify result."""
            try:
                unpacked = gl.vm.unpack_result(result)
                if not isinstance(unpacked, dict):
                    return False
                price_str = unpacked.get("price")
                if price_str:
                    price = float(price_str)
                    return price > 0 and price < 100000
                return False
            except Exception:
                return False
        
        # Run consensus
        try:
            data = gl.vm.run_nondet(leader, validator)
        except gl.vm.UserError:
            raise
        except Exception as e:
            raise gl.vm.UserError(f"update_price failed: {str(e)}")
        
        # Update state
        if not isinstance(data, dict):
            raise gl.vm.UserError("invalid result format")
        
        price_str = data.get("price")
        source_str = data.get("source", "unknown")
        
        try:
            self.last_price = float(price_str)
            _ = self.last_price
        except:
            raise gl.vm.UserError("price assignment error")
        
        self.last_source = source_str
        _ = self.last_source
```

### Key Management Workflow

1. **Add New Key**:
   ```python
   # Encrypt new key
   encrypted_new_key = encrypt_api_key("new-key-value")
   
   # Add to contract
   contract.add_api_key(encrypted_new_key)
   ```

2. **Monitor Key Health**:
   ```python
   # Check success counts
   status = contract.get_key_status()
   # Rotate manually if needed
   contract.rotate_key()
   ```

3. **Remove Old Key**:
   ```python
   # Mark as inactive or remove from list
   # (Requires contract update for removal)
   ```

---

## 🔒 Security Best Practices

### General Guidelines

1. **Never Hardcode Keys**: Always use environment variables or encrypted storage
2. **Use Read-Only Keys**: When possible, use API keys with minimal permissions
3. **Monitor Key Usage**: Track API calls per key, detect anomalies
4. **Rate Limiting**: Implement rate limits to prevent abuse
5. **Key Rotation**: Rotate keys regularly (every 90 days recommended)
6. **Audit Logs**: Log all API key usage for security monitoring

### Pattern-Specific Recommendations

**Off-chain Proxy**:
- Use HTTPS only
- Implement authentication for proxy endpoints
- Monitor proxy service uptime
- Use load balancing for high availability

**Encrypted On-chain**:
- Use strong encryption (AES-256 minimum)
- Secure decryption keys (HSM, secure enclaves)
- Regular encryption key rotation
- Limit leader node access

**Key Rotation**:
- Maintain at least 2 active keys
- Rotate keys proactively (before expiry)
- Test key rotation in staging first
- Monitor success rates per key

---

## 📊 Pattern Comparison

| Feature | Off-chain Proxy | Encrypted On-chain | Key Rotation |
|---------|----------------|-------------------|--------------|
| **Security** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Decentralization** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Key Privacy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Complexity** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost** | Medium (proxy) | Low | Medium |
| **Rotation Ease** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Recommendations

### When to Use Each Pattern

**Use Off-chain Proxy when**:
- Maximum security is required
- API keys are highly sensitive
- Proxy infrastructure is available
- Centralized trust is acceptable

**Use Encrypted On-chain when**:
- Decentralization is important
- No external dependencies desired
- Leader nodes are trusted and secure
- Simple key management is sufficient

**Use Key Rotation when**:
- High availability is critical
- Keys need frequent rotation
- Redundancy is required
- Multiple keys are available

### Hybrid Approach

Consider combining patterns:
- Use **Encrypted On-chain** with **Key Rotation** for best of both worlds
- Use **Off-chain Proxy** for sensitive keys, **Encrypted On-chain** for less sensitive data

---

## 📚 Further Reading

- [GenLayer Storage Documentation](https://docs.genlayer.com/developers/intelligent-contracts/storage)
- [GenLayer Non-deterministic Execution](https://docs.genlayer.com/developers/intelligent-contracts/non-deterministic-execution)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

---

## 📝 Examples Location

All example contracts are available in:
- `contracts/api-key-patterns/off-chain-proxy.py`
- `contracts/api-key-patterns/encrypted-onchain.py`
- `contracts/api-key-patterns/key-rotation.py`

