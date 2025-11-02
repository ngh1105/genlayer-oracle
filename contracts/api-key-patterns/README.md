# API Key Management Pattern Examples

This directory contains example contracts demonstrating different patterns for managing API keys in GenLayer contracts.

## 📚 Patterns

### 1. Off-chain Proxy Pattern
**File**: `off_chain_proxy_oracle.py`

- **Concept**: Contract calls proxy service that holds API keys
- **Security**: Keys never touch blockchain
- **Use Case**: Maximum security, easy key rotation

**Example**:
```python
# Deploy contract
contract = ProxyOracle()
contract.set_proxy_url("https://your-proxy.com/api")

# Update price (proxy handles API key)
contract.update_price("ETH")
```

**Proxy Service**: See `scripts/proxy-service-example.js`

### 2. Encrypted On-chain Pattern
**File**: `encrypted_onchain_oracle.py`

- **Concept**: API keys encrypted and stored on-chain
- **Security**: Only leader can decrypt during execution
- **Use Case**: No external dependencies, on-chain auditability

**Example**:
```python
# 1. Encrypt key off-chain
# python scripts/encrypt_key.py "your-api-key"
# Returns: encrypted_key_b64

# 2. Deploy contract and set encrypted key
contract = EncryptedKeyOracle()
contract.set_api_key(encrypted_key_b64)

# 3. Update price (leader decrypts key)
contract.update_price("ETH")
```

**Key Encryption**: See `scripts/encrypt_key.py`

### 3. Key Rotation Pattern
**File**: `key_rotation_oracle.py`

- **Concept**: Multiple keys with automatic rotation
- **Security**: Redundancy, zero-downtime rotation
- **Use Case**: High availability, frequent key rotation

**Example**:
```python
# 1. Add multiple encrypted keys
contract = RotatingKeyOracle()
contract.add_api_key(encrypted_key_1)
contract.add_api_key(encrypted_key_2)
contract.add_api_key(encrypted_key_3)

# 2. Update price (contract tries keys automatically)
contract.update_price("ETH")

# 3. Check key status
status = contract.get_key_status()
# Returns: active key, success counts, etc.
```

## 🚀 Quick Start

### Pattern 1: Off-chain Proxy

1. **Start Proxy Service**:
   ```bash
   cd scripts
   cp .env.example .env
   # Edit .env with your API keys
   npm install express axios dotenv
   node proxy-service-example.js
   ```

2. **Deploy Contract**:
   - Use `off_chain_proxy_oracle.py` in GenLayer Studio
   - Set proxy URL: `contract.set_proxy_url("http://your-proxy:3000/api")`

3. **Update Price**:
   ```python
   contract.update_price("ETH")
   ```

### Pattern 2: Encrypted On-chain

1. **Encrypt API Key**:
   ```bash
   python scripts/encrypt_key.py "your-api-key"
   # Copy the encrypted key output
   ```

2. **Deploy Contract**:
   - Use `encrypted_onchain_oracle.py` in GenLayer Studio
   - Set encrypted key: `contract.set_api_key("encrypted_key_b64...")`

3. **Update Price**:
   ```python
   contract.update_price("ETH")
   ```

### Pattern 3: Key Rotation

1. **Encrypt Multiple Keys**:
   ```bash
   python scripts/encrypt_key.py "api-key-1"
   python scripts/encrypt_key.py "api-key-2"
   python scripts/encrypt_key.py "api-key-3"
   ```

2. **Deploy Contract**:
   - Use `key_rotation_oracle.py` in GenLayer Studio
   - Add keys: `contract.add_api_key(encrypted_key_1)`, etc.

3. **Update Price** (automatic rotation on failure):
   ```python
   contract.update_price("ETH")
   ```

## 🔒 Security Notes

### General
- **Never hardcode keys**: Always use encryption or environment variables
- **Use read-only keys**: Minimize permissions when possible
- **Monitor usage**: Track API calls per key
- **Rotate regularly**: Change keys every 90 days

### Pattern-Specific

**Off-chain Proxy**:
- Use HTTPS only
- Implement authentication for proxy endpoints
- Monitor proxy uptime
- Use load balancing

**Encrypted On-chain**:
- Use strong encryption (AES-256, Fernet)
- Secure decryption keys (HSM, secure enclaves)
- Limit leader node access

**Key Rotation**:
- Maintain at least 2 active keys
- Test rotation in staging first
- Monitor success rates

## 📖 Documentation

See `docs/API_KEY_MANAGEMENT_PATTERNS.md` for:
- Detailed pattern explanations
- Architecture diagrams
- Security considerations
- Comparison table
- Best practices

## 🧪 Testing

Each pattern can be tested independently:

```python
# Test off-chain proxy
proxy = ProxyOracle()
proxy.set_proxy_url("http://localhost:3000/api")
proxy.update_price("ETH")
price = proxy.get_price()

# Test encrypted on-chain
encrypted = EncryptedKeyOracle()
encrypted.set_api_key(encrypted_key_b64)
encrypted.update_price("ETH")
price = encrypted.get_price()

# Test key rotation
rotation = RotatingKeyOracle()
rotation.add_api_key(key1)
rotation.add_api_key(key2)
rotation.update_price("ETH")
status = rotation.get_key_status()
```

## 📝 Notes

- All patterns use simplified encryption for demonstration
- In production, use proper encryption libraries (cryptography.fernet)
- Leader nodes must be trusted and secure
- Consider hybrid approaches for maximum security

