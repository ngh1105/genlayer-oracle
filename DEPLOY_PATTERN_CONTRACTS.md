# 🚀 Hướng Dẫn Deploy API Key Pattern Contracts

Để demo trực quan các API Key Management Patterns, bạn cần deploy các contracts và setup môi trường.

---

## 📋 Pattern Contracts Overview

| Pattern | Contract File | Setup Complexity | Recommended Order |
|---------|--------------|------------------|-------------------|
| **1. Encrypted On-chain** | `encrypted_onchain_oracle.py` | ⭐ Easy | Deploy đầu tiên (dễ nhất) |
| **2. Off-chain Proxy** | `off_chain_proxy_oracle.py` | ⭐⭐ Medium | Cần chạy proxy service |
| **3. Key Rotation** | `key_rotation_oracle.py` | ⭐⭐⭐ Hard | Cần nhiều keys |

---

## 🎯 Pattern 1: Encrypted On-chain Oracle (Dễ nhất - Khuyến nghị bắt đầu)

### Setup Steps

#### Step 1: Encrypt API Key
```bash
cd scripts
python encrypt_key.py "your-api-key-here"
```

**Output**: Bạn sẽ nhận được một encrypted key (base64 string), copy nó lại.

**Ví dụ output**:
```
Encrypted key (base64): gAAAAABl...xyz123==
```

#### Step 2: Deploy Contract
1. Mở GenLayer Studio
2. Tạo contract mới
3. Copy code từ `contracts/api-key-patterns/encrypted_onchain_oracle.py`
4. Deploy contract

#### Step 3: Set Encrypted API Key
Sau khi deploy, gọi method để set encrypted key:
```python
contract.set_api_key("gAAAAABl...xyz123==")
```

#### Step 4: Test Contract
```python
# Update price
contract.update_price("ETH")

# Check price
price = contract.get_price()
```

**✅ Done!** Contract đã sẵn sàng cho demo.

---

## 🎯 Pattern 2: Off-chain Proxy Oracle

### Setup Steps

#### Step 1: Setup Proxy Service

**Option A: Chạy local proxy**
```bash
cd scripts
npm install express axios dotenv

# Tạo .env file
cat > .env << EOF
COINGECKO_API_KEY=your-coingecko-key
BINANCE_API_KEY=your-binance-key
PORT=3000
HOST=0.0.0.0
EOF

# Chạy proxy
node proxy-service-example.js
```

**Option B: Deploy proxy lên server** (cho production)
- Deploy lên Heroku, Railway, hoặc VPS
- Update URL trong contract

#### Step 2: Verify Proxy Service
```bash
# Test health check
curl http://localhost:3000/health

# Test price endpoint
curl http://localhost:3000/api/price/ETH
```

**Expected Response**:
```json
{
  "price": "3500.50",
  "source": "coingecko-proxy",
  "timestamp": 1234567890,
  "symbol": "ETH"
}
```

#### Step 3: Deploy Contract
1. Mở GenLayer Studio
2. Tạo contract mới
3. Copy code từ `contracts/api-key-patterns/off_chain_proxy_oracle.py`
4. Deploy contract

#### Step 4: Set Proxy URL
```python
# Set proxy URL (local hoặc production URL)
contract.set_proxy_url("http://localhost:3000/api")
# hoặc
contract.set_proxy_url("https://your-proxy-service.com/api")
```

#### Step 5: Test Contract
```python
# Update price (contract gọi proxy)
contract.update_price("ETH")

# Check price
price = contract.get_price()
```

**✅ Done!** Contract gọi proxy service để fetch price.

---

## 🎯 Pattern 3: Key Rotation Oracle

### Setup Steps

#### Step 1: Encrypt Multiple API Keys
```bash
cd scripts

# Encrypt key 1
python encrypt_key.py "api-key-1"
# Copy output: encrypted_key_1 = "..."

# Encrypt key 2
python encrypt_key.py "api-key-2"
# Copy output: encrypted_key_2 = "..."

# Encrypt key 3 (optional)
python encrypt_key.py "api-key-3"
# Copy output: encrypted_key_3 = "..."
```

#### Step 2: Deploy Contract
1. Mở GenLayer Studio
2. Tạo contract mới
3. Copy code từ `contracts/api-key-patterns/key_rotation_oracle.py`
4. Deploy contract

#### Step 3: Add Encrypted Keys
```python
# Add multiple keys
contract.add_api_key("encrypted_key_1_base64...")
contract.add_api_key("encrypted_key_2_base64...")
contract.add_api_key("encrypted_key_3_base64...")  # Optional

# Check key status
status = contract.get_key_status()
# Returns: active key index, success counts, etc.
```

#### Step 4: Test Contract
```python
# Update price (contract tự động rotate keys nếu fail)
contract.update_price("ETH")

# Check price
price = contract.get_price()

# Check key rotation status
status = contract.get_key_status()
```

**✅ Done!** Contract tự động rotate keys khi một key fail.

---

## 📝 Deployment Checklist

### Cho Pattern 1 (Encrypted On-chain)
- [ ] Encrypt API key bằng `encrypt_key.py`
- [ ] Deploy contract trong GenLayer Studio
- [ ] Call `set_api_key(encrypted_key)`
- [ ] Test `update_price("ETH")`
- [ ] Verify `get_price()` returns correct data
- [ ] Save contract address

### Cho Pattern 2 (Off-chain Proxy)
- [ ] Setup proxy service (local hoặc production)
- [ ] Test proxy endpoints (`/health`, `/api/price/ETH`)
- [ ] Deploy contract trong GenLayer Studio
- [ ] Call `set_proxy_url(url)`
- [ ] Test `update_price("ETH")`
- [ ] Verify contract calls proxy successfully
- [ ] Save contract address

### Cho Pattern 3 (Key Rotation)
- [ ] Encrypt 2-3 API keys
- [ ] Deploy contract trong GenLayer Studio
- [ ] Call `add_api_key()` cho mỗi key
- [ ] Test `update_price("ETH")`
- [ ] Test key rotation (simulate key failure)
- [ ] Check `get_key_status()` để verify rotation
- [ ] Save contract address

---

## 📋 Sau Khi Deploy

### Update Documentation
Sau khi deploy thành công, update `DEPLOYED_CONTRACTS.md`:

```markdown
### 3. Encrypted On-chain Oracle
- **Contract Address**: `0x...`
- **Status**: ✅ Deployed for Demo
- **Pattern**: Encrypted on-chain API key storage

### 4. Off-chain Proxy Oracle
- **Contract Address**: `0x...`
- **Proxy Service**: `https://your-proxy.com`
- **Status**: ✅ Deployed for Demo
- **Pattern**: Off-chain proxy for API keys

### 5. Key Rotation Oracle
- **Contract Address**: `0x...`
- **Status**: ✅ Deployed for Demo
- **Pattern**: Automatic key rotation
```

### Update Frontend (Optional)
Có thể thêm support cho các pattern contracts trong frontend:
- Add contract addresses
- Add UI cho từng pattern
- Show key rotation status (cho Pattern 3)

---

## 🔧 Troubleshooting

### Pattern 1 Issues
**Problem**: `encrypted key cannot be empty`
- **Solution**: Ensure `set_api_key()` was called with valid encrypted key

**Problem**: `decryption failed`
- **Solution**: Verify encryption was done correctly with same script

### Pattern 2 Issues
**Problem**: `proxy service unavailable`
- **Solution**: Check proxy service is running (`curl http://localhost:3000/health`)
- **Solution**: Verify proxy URL is correct (no trailing slash)

**Problem**: `proxy request failed`
- **Solution**: Check proxy service logs
- **Solution**: Verify API keys in proxy `.env` file

### Pattern 3 Issues
**Problem**: `no active keys`
- **Solution**: Ensure `add_api_key()` was called at least once

**Problem**: All keys failing
- **Solution**: Verify all keys are valid and properly encrypted
- **Solution**: Check external API is accessible

---

## 💡 Recommendations

### Để Demo Tốt Nhất:

1. **Start với Pattern 1** (Encrypted On-chain)
   - Dễ nhất, không cần external services
   - Quick demo trong 5-10 phút

2. **Sau đó Pattern 2** (Off-chain Proxy)
   - Show proxy architecture
   - Demonstrate security benefits

3. **Cuối cùng Pattern 3** (Key Rotation)
   - Most complex but most powerful
   - Show automatic failover

### Production Considerations:
- **Pattern 1**: Use proper encryption (AES-256, Fernet)
- **Pattern 2**: Deploy proxy on reliable infrastructure (Heroku, Railway)
- **Pattern 3**: Monitor key success rates, setup alerts

---

## ✅ Ready to Deploy?

1. Chọn pattern muốn deploy (1, 2, hoặc cả 3)
2. Follow setup steps ở trên
3. Test thoroughly
4. Update `DEPLOYED_CONTRACTS.md`
5. Share contract addresses để demo

**Estimated Time**:
- Pattern 1: 10-15 phút
- Pattern 2: 20-30 phút (nếu cần setup proxy)
- Pattern 3: 15-20 phút

---

**Last Updated**: 2025-11-02

