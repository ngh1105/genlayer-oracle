# API Clients vs Contract: Khi nào dùng gì?

## Tình huống 1: Chỉ cần hiển thị data trên frontend

**Dùng API clients** ✅
```typescript
// Đơn giản, nhanh, không cần deploy contract
const price = await api.priceClient.getPrice('ETH');
console.log(price); // Hiển thị ngay
```

## Tình huống 2: Cần data trong smart contract khác

**Dùng Contract** ✅
```python
# Contract A cần price từ Oracle
class MyContract(gl.Contract):
    def do_something(self):
        # Cần đọc từ Oracle contract
        oracle = OracleConsumer(address="0x...")
        price = oracle.get_status()["price"]["eth_usd"]
        # Sử dụng price trong logic on-chain
```

## Tình huống 3: Cần data đáng tin cậy với consensus

**Dùng Contract** ✅
- API client: Chỉ một client fetch → không đảm bảo
- Contract: Leader fetch + Validators verify → có consensus, đáng tin hơn

## Tình huống 4: Cần lịch sử data

**Dùng Contract** ✅
- API client: Mỗi lần fetch mới, không lưu lại
- Contract: State persist on-chain, có thể query lịch sử

## Tình huống 5: Cần data để tính toán on-chain

**Dùng Contract** ✅
```python
# DeFi protocol cần price để tính toán
class DeFiProtocol(gl.Contract):
    def calculate_loan(self, collateral):
        oracle_price = oracle.get_status()["price"]["eth_usd"]
        loan_amount = collateral * float(oracle_price) * 0.8
        # Logic on-chain với data từ oracle
```

## Kết luận

**API Clients**: 
- ✅ Đơn giản, nhanh
- ✅ Không cần deploy
- ❌ Không có consensus
- ❌ Không persistent
- ❌ Không trustless

**Contract**:
- ✅ Decentralized với consensus
- ✅ Persistent on-chain
- ✅ Trustless
- ✅ Có thể dùng trong contracts khác
- ❌ Cần deploy và chờ consensus (chậm hơn)

**Khuyến nghị**: 
- **Demo/Testing/Frontend đơn giản** → Dùng API clients
- **Production dApp/Smart contracts/DeFi** → Dùng Contract với consensus

