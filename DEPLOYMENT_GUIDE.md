# Deployment Guide - Web Fetcher Library

## 🎯 Next Step: Deploy & Test on Studionet

### Goal
Deploy example contract sử dụng Web Fetcher library để verify hoạt động trên GenLayer studionet.

## 📋 Preparation

### Files Needed

1. **Library**: `packages/genvm-web-fetcher/web_fetcher.py`
2. **Example**: `packages/genvm-web-fetcher/examples/simple_price_feed.py`

### Contract to Deploy

**File**: `simple_price_feed.py`

**Features**:
- Uses `PriceFeedPattern` from web_fetcher
- Fetches ETH price from Binance → Coingecko fallback
- Simple state persistence
- Easy to test

## 🚀 Deployment Steps

### Step 1: Copy Files to GenLayer Studio

1. Open GenLayer Studio
2. Create new contract file
3. Copy content từ `web_fetcher.py` vào project
4. Copy content từ `simple_price_feed.py` vào project
5. Ensure imports work: `from web_fetcher import PriceFeedPattern`

### Step 2: Deploy Contract

1. Deploy contract lên studionet
2. **Save contract address** (cần để test)
3. Wait for deployment confirmation

### Step 3: Test Contract

#### Test 1: Update Price
- Call `update_price()` method
- Parameters: None (uses defaults)
- Wait for consensus (PENDING → FINALIZED)
- Check transaction status

#### Test 2: Read Price
- Call `get_price()` method
- Verify returns:
  ```python
  {
    "price": "3862.79",  # ETH price as string
    "source": "binance"  # or "coingecko"
  }
  ```

#### Test 3: Verify Fallback
- (Optional) If có cách simulate Binance failure
- Verify falls back to Coingecko
- Check source changes to "coingecko"

## ✅ Success Criteria

- [ ] Contract deploys successfully
- [ ] `update_price()` executes và FINALIZED
- [ ] `get_price()` returns valid price data
- [ ] Price value > 0 and reasonable (ETH ~$3000-4000)
- [ ] Source is "binance" or "coingecko"
- [ ] State persists (call get_price multiple times, same value)

## 📊 Expected Results

### Successful Deployment
```
Contract Address: 0x...
Status: Deployed ✅

Transaction (update_price):
- Status: FINALIZED ✅
- Execution: SUCCESS ✅
- Consensus: ACCEPTED ✅

Result (get_price):
{
  "price": "3862.79",
  "source": "binance"
}
```

## 🐛 Troubleshooting

### Issue: Import Error
**Error**: `Cannot find module 'web_fetcher'`

**Solution**: 
- Ensure `web_fetcher.py` is in same directory
- Or adjust import path

### Issue: Price is 0 or invalid
**Possible causes**:
- All sources failed
- Validator rejected result
- State not persisted

**Check**:
- Transaction logs for errors
- Equivalence Principles output
- Validator consensus status

### Issue: Consensus Failed
**Possible causes**:
- Validator couldn't verify data
- Network issues
- Invalid response format

**Check**:
- Leader execution logs
- Validator votes
- Error messages in transaction

## 📝 Documentation

After successful deployment, document:

1. **Contract Address**: `0x...`
2. **Deployment Date**: `YYYY-MM-DD`
3. **Test Results**: 
   - Update time: `X seconds`
   - Price fetched: `$XXXX.XX`
   - Source used: `binance/coingecko`
4. **Screenshots**: Transaction details, results

## 🎉 Next Steps After Deployment

Once deployment successful:

1. ✅ **Document Results**: Add to `TEST_RESULTS.md`
2. ✅ **Submit Contribution**: Library ready for Tools & Infrastructure
3. ✅ **Move to Oracle SDK**: Complete SDK setup
4. ✅ **Start Research**: Begin performance benchmarks

## Expected Points

**Web Fetcher Library**: 200-500 pts (Tools & Infrastructure)

---

**Ready to deploy?** Follow steps above và document results!

