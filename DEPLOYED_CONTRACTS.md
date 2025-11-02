# Deployed Contracts - GenLayer Oracle

## ✅ Deployed Contracts on studionet

### 1. Simple Price Feed
- **Contract Address**: `0xe328378CAF086ae0a6458395C9919a4137fCb888`
- **Status**: ✅ Deployed and Working
- **Features**:
  - ETH price fetching from Binance/Coingecko
  - State persistence ✅
  - Simple, focused contract

**Methods**:
- `get_price() -> dict`: Returns `{"price": str, "source": str}`
- `update_price() -> None`: Fetches and stores ETH price
- `debug_state() -> dict`: Debug state information

### 2. Oracle Consumer (Full Oracle)
- **Contract Address**: `0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`
- **Status**: ✅ Deployed and Ready
- **Features**:
  - ETH price fetching (Binance/Coingecko)
  - Weather data (Open-Meteo)
  - News count (Reddit/CoinDesk RSS)
  - State persistence ✅
  - Comprehensive oracle

**Methods**:
- `get_status() -> dict`: Returns all oracle data
  ```json
  {
    "price": {"eth_usd": str, "source": str},
    "weather": {"temperature": str, "condition": str, "city": str},
    "news": {"count": int}
  }
  ```
- `update_all(city, lat, lon, news_limit) -> None`: Fetches and stores all data
- `debug_state() -> dict`: Debug state information

## Frontend Integration

Both contracts are supported in the frontend:
- Switch between "Simple Price Feed" and "Oracle Consumer" using dropdown
- Simple Price Feed address is pre-filled
- Oracle Consumer address: `0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`

## Testing

### Simple Price Feed
1. Address: `0xe328378CAF086ae0a6458395C9919a4137fCb888`
2. Call `update_price()` → Wait FINALIZED
3. Call `get_price()` → Should return updated price

### Oracle Consumer
1. Address: `0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`
2. Call `update_all("Hanoi", "21.0245", "105.8412", 3)` → Wait FINALIZED
3. Call `get_status()` → Should return price, weather, news

## Key Learnings Applied

1. **State Persistence**: Fields MUST be declared in class body with type annotations
2. **Type Restrictions**: Can't use plain `int`, use `str`, `float`, `bigint`, or sized integers
3. **Event Classes**: GenLayer Event syntax is complex - removed for simplicity
4. **Multi-source Fallback**: Essential for reliability (Binance mirrors → Coingecko)

---

**Deployment Date**: Successfully deployed and tested
**Network**: studionet
**Status**: ✅ Both contracts production-ready

