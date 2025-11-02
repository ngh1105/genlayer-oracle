# State Persistence Analysis

## Problem Summary

- ✅ `update_price()` transaction FINALIZED successfully
- ✅ Equivalence Principles Output has correct data: `{"price":"3898.23","source":"binance"}`
- ✅ 6 validators agreed (consensus passed)
- ❌ But `get_price()` and `debug_state()` still return `0.0` and `""`

**Transaction Output `6`** = Number of validators who agreed (NOT method return value)

## Code Comparison

### Current Code (simple_price_feed_complete.py)
```python
# Unpack result
unpacked = gl.vm.unpack_result(result)

# Extract and parse
price_val = float(str(price_str))
source_val = str(source_str)

# Assign
self.last_price = price_val
self.last_source = source_val

# Read to trigger tracking
stored_price = self.last_price
stored_source = self.last_source

# Verify
if stored_price != price_val:
    raise gl.vm.UserError(f"price assignment failed")
```

### Working Code (oracle_consumer.py)
```python
# Parse and assign
price_float = float(str(price_val))
self.last_eth_price = price_float
# Force storage write by reassigning
_ = self.last_eth_price
```

**They are essentially the same!** Both use:
- Direct assignment: `self.field = value`
- Dummy read: `_ = self.field`

## Possible Root Causes

### 1. Assignment Code Not Executing
- Exception might be caught silently
- Code might not reach assignment line
- Need to verify with better error handling

### 2. GenLayer State Tracking Issue
- Assignment happens but GenLayer doesn't track it
- Might need different approach for simple contracts
- Could be a bug in GenLayer for this contract type

### 3. View Method Snapshot Issue
- View methods might read from snapshot before write finalizes
- State exists but view reads old snapshot
- Need to verify with write method read

### 4. Contract Instance Isolation
- Each transaction might use isolated instance
- State not shared between transactions
- Need to verify contract address consistency

## Diagnostic Steps

1. **Check if assignment code runs**:
   - Add more explicit error messages
   - Check transaction logs for any errors

2. **Try reading from write method**:
   - Call `update_price()` then immediately read in same transaction
   - Or use a combined method

3. **Verify contract address**:
   - Ensure same address for write and read
   - Check if contract is redeployed

4. **Compare with oracle_consumer**:
   - If oracle_consumer works, what's different?
   - Check initialization, assignment pattern, etc.

## Next Fix to Try

Add explicit error checking and try alternative assignment pattern:

```python
# After unpack_result
# ... parse values ...

# Assignment with explicit tracking
self.last_price = price_val
_ = self.last_price  # Must be on separate line

self.last_source = source_val  
_ = self.last_source  # Must be on separate line

# No verification - let it fail naturally if wrong
```

If this still doesn't work, might be a GenLayer storage mechanism issue that needs platform support.

