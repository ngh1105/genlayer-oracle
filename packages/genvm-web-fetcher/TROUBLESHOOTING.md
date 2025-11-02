# Troubleshooting: get_price() Returns 0

## Current Issue
`update_price()` FINALIZED successfully, but `get_price()` returns `{"price": "0.0", "source": ""}`

## 🔍 Debug Steps

### Step 1: Check Transaction Output

**Trong GenLayer Studio**, mở transaction `update_price()` đã FINALIZED:

1. Click vào transaction `0xb6e5... update_price`
2. Tìm phần **"Equivalence Principles Output"** hoặc **"Output"**
3. Kiểm tra có data không:
   ```json
   {"price": "3862.79", "source": "binance"}
   ```

**Nếu có data trong Equivalence Principles**:
- ✅ Leader đã fetch được data
- ✅ Validator đã accept
- ❌ Vấn đề ở phần assignment/persistence

**Nếu KHÔNG có data**:
- ❌ Leader hoặc validator failed
- ❌ Cần check transaction logs

### Step 2: Use debug_state() Method

Contract đã có method `debug_state()`:

1. Call `debug_state()` sau khi `update_price()` FINALIZED
2. Check kết quả:
   ```json
   {
     "has_price": true/false,
     "price_value": "...",
     "has_source": true/false,
     "source_value": "..."
   }
   ```

**Nếu `has_price: false` hoặc `price_value: "NOT_SET"`**:
- Attributes không tồn tại → State không được persist

**Nếu `has_price: true` nhưng `price_value: "0.0"`**:
- Attributes tồn tại nhưng giá trị là 0 → Assignment không chạy

### Step 3: Verify Contract Address

1. Kiểm tra contract address khi deploy
2. Kiểm tra address khi gọi `get_price()`
3. **Nếu khác nhau** → Contract đang được deploy lại mỗi lần

## 🛠️ Fixes Applied

### Fix 1: Added Dummy Reads
```python
self.last_price = price_val
_ = self.last_price  # Trigger tracking

self.last_source = source_val
_ = self.last_source  # Trigger tracking
```

### Fix 2: Added debug_state() Method
```python
@gl.public.view
def debug_state(self) -> dict:
    return {
        "has_price": hasattr(self, 'last_price'),
        "price_value": str(getattr(self, 'last_price', 'NOT_SET')),
        ...
    }
```

## 📋 Next Actions

1. **Check Equivalence Principles output** trong transaction
2. **Call `debug_state()`** và xem kết quả
3. **Verify contract address** consistency
4. **Report back** với kết quả

## Possible Root Causes

### 1. Contract Address Changes
- Each call uses different contract instance
- Solution: Ensure same contract address

### 2. State Not Tracked
- GenLayer không track assignment
- Solution: Dummy reads (đã apply)

### 3. Transaction Output Missing
- `run_nondet()` không return data
- Solution: Check Equivalence Principles

### 4. Assignment Outside Transaction Context
- State changes không được commit
- Solution: Ensure in write method context

---

**Please check Equivalence Principles output và call debug_state()**, sau đó report kết quả!

