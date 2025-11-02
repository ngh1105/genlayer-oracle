# OracleConsumer Contract

GenLayer decentralized oracle contract that fetches real-world data using non-deterministic execution.

## Overview

The `OracleConsumer` contract demonstrates GenLayer's capability to fetch off-chain data while maintaining blockchain consensus through leader-validator agreement.

## Contract Interface

### Write Methods

**`update_all(city: str, lat: str, lon: str, news_limit: int) -> None`**

Fetches and updates all oracle data:
- **Parameters**:
  - `city`: City name (default: "Hanoi")
  - `lat`: Latitude as string (default: "21.0245")
  - `lon`: Longitude as string (default: "105.8412")
  - `news_limit`: Number of news items to fetch (default: 3)
- **Process**:
  1. Leader node fetches data from APIs
  2. Validators verify the data through consensus
  3. If consensus passes, state is updated and event is emitted
- **Data Sources**:
  - Price: Binance (6 mirrors) → Coingecko fallback
  - Weather: Open-Meteo API
  - News: Reddit → CoinDesk RSS fallback

### View Methods

**`get_status() -> dict`**

Returns current oracle state:
```python
{
  "price": {"eth_usd": str, "source": str},
  "weather": {"temperature": str, "condition": str, "city": str},
  "news": {"count": int}
}
```

**`debug_state() -> dict`**

Debug method to check state persistence (development only).

### Events

**`OracleUpdateEvent(price, source, temperature, city, news_count)`**

Emitted when data is successfully updated.

## Consensus Mechanism

Uses `gl.vm.run_nondet(leader, validator)`:
- **Leader**: Fetches data from APIs
- **Validator**: Verifies data integrity (checks format, ranges, etc.)
- **Consensus**: Both must agree for state update to occur

## Error Handling

- All API errors converted to `gl.vm.UserError` for proper handling
- Fallback mechanisms for rate-limited APIs
- Comprehensive validation in both leader and validator functions

## State Persistence

State is stored in contract instance attributes:
- `last_eth_price`: Latest ETH/USD price
- `last_eth_source`: Data source identifier
- `last_weather_*`: Weather data fields
- `last_news_count`: Latest news count

**Note**: Ensure contract uses a fixed address across transactions for proper state persistence.




