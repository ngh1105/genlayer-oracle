# Testing Guide - Simple Price Feed Contract

## Contract Address
**Deployed at:** `0xe328378CAF086ae0a6458395C9919a4137fCb888`

## ✅ Critical Fix Applied

Fields are now declared in class body with type annotations:
```python
class SimplePriceFeed(gl.Contract):
    last_price: float  # ✅ Persistent field
    last_source: str   # ✅ Persistent field
```

This ensures state persistence according to GenLayer documentation.

## Testing Steps

### Step 1: Initial State Check

1. **Call `debug_state()`** method (view)
   - Expected result:
     ```json
     {
       "has_price": true,
       "price_value": "0.0",
       "price_type": "float",
       "has_source": true,
       "source_value": "",
       "contract_address": "0xe328378CAF086ae0a6458395C9919a4137fCb888"
     }
     ```

2. **Call `get_price()`** method (view)
   - Expected result:
     ```json
     {
       "price": "0.0",
       "source": ""
     }
     ```

### Step 2: Update Price

1. **Call `update_price()`** method (write)
   - Parameters: None required
   - Wait for transaction to FINALIZE
   - Expected transaction status: SUCCESS, FINALIZED
   - Expected consensus: ACCEPTED (multiple validators agree)
   - Expected Equivalence Principles Output:
     ```json
     {"price": "3800-4000", "source": "binance"}
     ```
     (Actual price will vary based on current ETH price)

### Step 3: Verify State Persistence

**After `update_price()` FINALIZED:**

1. **Call `debug_state()`** again
   - Expected result (example):
     ```json
     {
       "has_price": true,
       "price_value": "3898.23",  // ✅ Updated value!
       "price_type": "float",
       "has_source": true,
       "source_value": "binance",  // ✅ Updated value!
       "contract_address": "0xe328378CAF086ae0a6458395C9919a4137fCb888"
     }
     ```

2. **Call `get_price()`** again
   - Expected result (example):
     ```json
     {
       "price": "3898.23",  // ✅ Updated value!
       "source": "binance"   // ✅ Updated value!
     }
     ```

## ✅ Success Criteria

All of these must pass:

- [ ] Contract deploys without errors
- [ ] `update_price()` transaction FINALIZED successfully
- [ ] `debug_state()` shows `price_value` > 0 after update
- [ ] `debug_state()` shows `source_value` is "binance" or "coingecko" after update
- [ ] `get_price()` returns valid price data after update
- [ ] State persists across multiple calls (call `get_price()` multiple times, should return same value)

## 🔍 If State Still Not Persisting

If state is still `0.0` after update:

1. **Verify contract address**: Ensure you're calling methods on the correct contract
   - Address should be: `0xe328378CAF086ae0a6458395C9919a4137fCb888`

2. **Check transaction status**: Ensure `update_price()` transaction is FINALIZED (not just ACCEPTED)

3. **Wait a few seconds**: Sometimes there's a delay between FINALIZED and state being readable

4. **Check Equivalence Principles**: Verify data exists in transaction output

5. **Verify code**: Ensure deployed code has type annotations in class body:
   ```python
   class SimplePriceFeed(gl.Contract):
       last_price: float  # Must be here!
       last_source: str   # Must be here!
   ```

## 📊 Expected Transaction Details

### update_price() Transaction:
- **Status**: FINALIZED ✅
- **Execution**: SUCCESS ✅
- **Consensus**: ACCEPTED ✅
- **Equivalence Principles Output**: `{"price": "...", "source": "binance"}` ✅
- **Result**: Number of validators who agreed (e.g., `6`)

### debug_state() After Update:
- **price_value**: Should be actual ETH price (3000-4000 range) ✅
- **source_value**: Should be "binance" or "coingecko" ✅

### get_price() After Update:
- **price**: Should match `price_value` from `debug_state()` ✅
- **source**: Should match `source_value` from `debug_state()` ✅

---

**Good luck with testing!** 🚀

