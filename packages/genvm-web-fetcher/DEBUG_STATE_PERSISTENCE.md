# Debug: State Persistence Issue

## Problem
`update_price()` FINALIZED successfully, but `get_price()` still returns `{"price": "0.0", "source": ""}`

## Possible Causes

### 1. Contract Instance Issue
- Contract address changes between calls
- Each call creates new instance → state lost

### 2. State Assignment Not Persisted
- Assignment happens but not tracked
- GenLayer storage system needs explicit tracking

### 3. Transaction Output Check
- Check Equivalence Principles output in transaction details
- Verify data was actually returned from `run_nondet()`

## Debugging Steps

### Step 1: Check Transaction Details
In GenLayer Studio, check the `update_price()` transaction:
1. Open transaction details
2. Check "Equivalence Principles Output"
3. Verify data is present: `{"price": "...", "source": "..."}`

**If data is in Equivalence Principles** → Assignment issue
**If data is NOT in Equivalence Principles** → Leader/validator issue

### Step 2: Verify Contract Address
1. Note contract address when deploying
2. Check if address is same when calling `get_price()`
3. If different → contract being redeployed

### Step 3: Add Debug Method
Add a debug method to check state:
```python
@gl.public.view
def debug_state(self) -> dict:
    return {
        "has_price": hasattr(self, 'last_price'),
        "price_value": str(getattr(self, 'last_price', 'NOT_SET')),
        "has_source": hasattr(self, 'last_source'),
        "source_value": getattr(self, 'last_source', 'NOT_SET'),
    }
```

Call this after `update_price()` to see if attributes exist.

## Current Fix Applied

Added dummy reads to trigger tracking:
```python
self.last_price = price_val
_ = self.last_price  # Trigger tracking

self.last_source = source_val
_ = self.last_source  # Trigger tracking
```

## Next Steps

1. **Check transaction Equivalence Principles output**
   - If data exists there → Assignment problem
   - If data missing → Leader/validator problem

2. **Add debug_state() method** and call it after update_price()

3. **Verify contract address consistency**

## If Still Not Working

Possible solutions:
1. Use separate fields instead of nested data
2. Add explicit storage types (if GenLayer supports)
3. Emit event and check event data
4. Use contract address verification in get_price()

