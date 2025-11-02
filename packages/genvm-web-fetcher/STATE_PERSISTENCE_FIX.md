# State Persistence Fix - get_price() Returns 0

## Problem Confirmed
- ✅ Transaction `update_price()` FINALIZED successfully
- ✅ Equivalence Principles Output has data: `{"price":"3874.65","source":"binance"}`
- ❌ But `get_price()` returns `{"price": "0.0", "source": ""}`

## Root Cause Analysis

**Data exists in Equivalence Principles** → Leader và validator hoạt động ✅
**State không persist** → Vấn đề ở assignment/persistence ❌

### Possible Causes:

1. **Contract Address Mismatch** (Most Likely)
   - Write transaction uses contract address A
   - Read transaction uses contract address B
   - Each has separate state → state không match

2. **State Not Committed**
   - Assignment happens but not committed to storage
   - GenLayer storage system không track properly

3. **View Method Reads from Different Snapshot**
   - View methods read from snapshot before write
   - Need to wait or use different transaction variant

## Fixes Applied

### Fix 1: Enhanced Assignment with Validation
```python
# Safe unpacking and assignment
if not isinstance(data, dict):
    raise gl.vm.UserError("invalid result format")

price_str = data.get("price")
source_str = data.get("source")

# Parse and assign with error handling
price_val = float(str(price_str))
source_val = str(source_str)

self.last_price = price_val
_ = self.last_price  # Trigger tracking

self.last_source = source_val
_ = self.last_source  # Trigger tracking

# Verify assignment worked
if self.last_price != price_val or self.last_source != source_val:
    raise gl.vm.UserError("state assignment failed")
```

### Fix 2: Enhanced debug_state()
```python
@gl.public.view
def debug_state(self) -> dict:
    return {
        "has_price": hasattr(self, 'last_price'),
        "price_value": str(self.last_price),
        "price_type": type(self.last_price).__name__,
        "has_source": hasattr(self, 'last_source'),
        "source_value": self.last_source,
        "contract_address": str(self.address) if hasattr(self, 'address') else 'NO_ADDRESS',
    }
```

## Diagnostic Steps

### Step 1: Check Contract Address
1. Note contract address khi deploy
2. Note address khi gọi `update_price()`
3. Note address khi gọi `get_price()`
4. **Compare**: Nếu khác nhau → Đây là nguyên nhân!

### Step 2: Call debug_state()
1. Gọi `debug_state()` sau khi `update_price()` FINALIZED
2. Check `contract_address` field
3. Check `price_value` và `has_price`

**Nếu `has_price: false`**:
- Attributes không tồn tại
- State không được persist

**Nếu `has_price: true` nhưng `price_value: "0.0"`**:
- Attributes tồn tại nhưng giá trị là 0
- Assignment không chạy hoặc không persist

**Nếu `contract_address` khác nhau**:
- Contract đang được deploy lại
- State bị mất giữa các calls

### Step 3: Verify Transaction Finalization
1. Đảm bảo `update_price()` transaction is **FINALIZED** (không chỉ ACCEPTED)
2. Đợi vài giây sau FINALIZED
3. Sau đó mới gọi `get_price()`

## Next Steps

1. **Deploy lại contract** với code mới (đã có fixes)
2. **Gọi `update_price()`** → Đợi FINALIZED
3. **Gọi `debug_state()`** → Check results
4. **Verify contract address** consistency
5. **Gọi `get_price()`** → Check if works now

## Expected Results After Fix

### debug_state() After update_price():
```json
{
  "has_price": true,
  "price_value": "3874.65",  // Actual price
  "price_type": "float",
  "has_source": true,
  "source_value": "binance",
  "contract_address": "0x..."  // Should be consistent
}
```

### get_price() After update_price():
```json
{
  "price": "3874.65",
  "source": "binance"
}
```

---

**Please deploy lại contract với code mới và test!** 🚀

