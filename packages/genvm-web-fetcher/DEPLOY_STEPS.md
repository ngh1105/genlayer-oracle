# Step-by-Step Deployment Guide

## 📋 Pre-Deployment Checklist

- [ ] GenLayer Studio account ready
- [ ] Access to studionet
- [ ] Contract file ready (`simple_price_feed_complete.py`)

## 🚀 Deployment Steps

### Step 1: Open GenLayer Studio

1. Go to GenLayer Studio (your studionet URL)
2. Navigate to Contracts section
3. Click "New Contract" or "Deploy Contract"

### Step 2: Copy Contract Code

1. Open file: `packages/genvm-web-fetcher/DEPLOY_READY/simple_price_feed_complete.py`
2. **Select ALL content** (Ctrl+A / Cmd+A)
3. **Copy** (Ctrl+C / Cmd+C)
4. Paste into GenLayer Studio contract editor

### Step 3: Deploy Contract

1. In GenLayer Studio:
   - Contract name: `SimplePriceFeed` (or any name you want)
   - Network: **studionet**
   - Click "Deploy" or "Create Contract"
2. Wait for deployment to complete
3. **IMPORTANT**: Copy and save the contract address (e.g., `0x...`)
4. Note deployment transaction hash

### Step 4: Test Contract - Update Price

1. In GenLayer Studio, find your deployed contract
2. Go to "Write Methods" section
3. Find `update_price()` method
4. Click "Send Transaction" or "Call Method"
   - Parameters: None needed (method has no parameters)
5. Wait for transaction:
   - Status: PENDING → PROPOSING → COMMITTING → REVEALING → **FINALIZED**
   - Execution: SUCCESS
6. Note the transaction hash

### Step 5: Test Contract - Read Price

1. After `update_price()` is FINALIZED, go to "Read Methods"
2. Find `get_price()` method
3. Click "Call Contract" (no parameters needed)
4. Check the response:
   ```json
   {
     "price": "3862.79",  // ETH price as string
     "source": "binance"  // or "coingecko"
   }
   ```
5. Verify:
   - Price > 0 ✅
   - Price is reasonable (ETH ~$3000-4000) ✅
   - Source is "binance" or "coingecko" ✅

### Step 6: Verify State Persistence

1. Call `get_price()` multiple times
2. Verify it returns the same value (not resetting)
3. If values persist → State persistence works! ✅

## ✅ Success Criteria

All of these should pass:

- [ ] Contract deploys without errors
- [ ] `update_price()` transaction FINALIZED successfully
- [ ] `get_price()` returns valid price data
- [ ] Price value > 0 and reasonable ($3000-4000 range)
- [ ] Source is either "binance" or "coingecko"
- [ ] State persists (multiple calls return same value)

## 📊 Expected Results

### Successful Deployment

**Contract Info**:
```
Contract Name: SimplePriceFeed
Contract Address: 0x[YOUR_ADDRESS]
Network: studionet
Status: Deployed ✅
```

**Transaction (update_price)**:
```
Transaction Hash: 0x[TX_HASH]
Status: FINALIZED ✅
Execution: SUCCESS ✅
Consensus: ACCEPTED ✅
Gas Used: [number]
```

**Read Result (get_price)**:
```json
{
  "price": "3862.79",
  "source": "binance"
}
```

## 🐛 Troubleshooting

### Issue: Contract Won't Deploy

**Error**: Syntax error, import error, etc.

**Solution**:
- Check you copied the ENTIRE file content
- Verify no characters were lost
- Check GenLayer Studio console for specific errors

### Issue: update_price() Fails

**Error**: Transaction reverted, consensus failed

**Possible causes**:
- Network issues with Binance/Coingecko APIs
- Validator rejected invalid data
- Rate limiting

**Check**:
- Transaction logs/events
- Equivalence Principles output
- Validator consensus details

### Issue: get_price() Returns Default Values

**Problem**: Returns `{"price": "0.0", "source": ""}`

**Possible causes**:
- `update_price()` hasn't been called yet
- `update_price()` failed silently
- State not persisting

**Solution**:
- Call `update_price()` first
- Wait for FINALIZED status
- Then call `get_price()`

### Issue: Price is 0 or Invalid

**Check**:
1. Did `update_price()` FINALIZE successfully?
2. Check transaction logs for errors
3. Check Equivalence Principles output
4. Verify API sources are accessible

## 📝 Documentation Template

After successful deployment, fill this out:

```markdown
## Deployment Results

**Date**: [YYYY-MM-DD]
**Contract Address**: [0x...]
**Network**: studionet

### Test Results

**update_price()**:
- Transaction Hash: [0x...]
- Status: FINALIZED
- Time to Finalize: [X seconds]
- Gas Used: [number]

**get_price()**:
- Price: $[XXXX.XX]
- Source: [binance/coingecko]
- Timestamp: [time]

### Notes
[Any observations or issues]
```

## 🎉 Next Steps After Success

Once deployment successful:

1. ✅ Document results (use template above)
2. ✅ Take screenshots of:
   - Deployment confirmation
   - Transaction details
   - get_price() results
3. ✅ Update `TEST_RESULTS.md` with deployment info
4. ✅ Library ready for Tools & Infrastructure contribution!
5. ✅ Expected points: **200-500 pts**

---

**Ready?** Follow steps above và let me know results! 🚀

