# 🚀 Quick Deploy - Web Fetcher Test Contract

## File Ready to Deploy

**Location**: `packages/genvm-web-fetcher/DEPLOY_READY/simple_price_feed_complete.py`

**What it is**: Complete contract file với WebFetcher library embedded - copy & paste ready!

## 📋 Quick Steps (5 minutes)

### 1. Open File
```
packages/genvm-web-fetcher/DEPLOY_READY/simple_price_feed_complete.py
```

### 2. Copy All Content
- Select ALL (Ctrl+A / Cmd+A)
- Copy (Ctrl+C / Cmd+C)

### 3. Paste vào GenLayer Studio
- Open GenLayer Studio
- New Contract / Deploy Contract
- Paste code vào editor

### 4. Deploy
- Network: **studionet**
- Click Deploy
- **Save contract address**: `0x...`

### 5. Test
- Call `update_price()` → Wait FINALIZED
- Call `get_price()` → Check result

## ✅ Expected Result

```json
{
  "price": "3862.79",  // ETH price
  "source": "binance"  // or "coingecko"
}
```

## 📖 Detailed Guide

See: `packages/genvm-web-fetcher/DEPLOY_STEPS.md` for complete instructions

## 🎯 What This Tests

- ✅ WebFetcher library hoạt động
- ✅ Multi-source fallback (Binance → Coingecko)
- ✅ Consensus mechanism
- ✅ State persistence

---

**Ready?** Copy file và deploy! 🚀

