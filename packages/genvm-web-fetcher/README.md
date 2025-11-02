# GenVM Web Fetcher

A reusable library for fetching data from external APIs in GenVM Python contracts with built-in error handling, retry logic, and multi-source fallback mechanisms.

## Features

- ✅ **Multi-source fallback**: Try multiple endpoints with automatic fallback
- ✅ **Error handling**: Comprehensive error handling with proper exception types
- ✅ **Retry logic**: Configurable retry with exponential backoff
- ✅ **Response validation**: Built-in validators for common patterns
- ✅ **Common patterns**: Pre-built patterns for price feeds, weather, news

## Installation

Copy the `web_fetcher.py` file into your GenVM contract project and import:

```python
# In your contract file header
# { "Depends": "py-genlayer:latest" }
import genlayer.gl as gl
from web_fetcher import WebFetcher, PriceFeedPattern, WeatherPattern
```

## Quick Start

### Basic Usage

```python
from web_fetcher import WebFetcher

def leader():
    fetcher = WebFetcher()
    
    # Simple GET request
    resp = fetcher.get(
        "https://api.example.com/data",
        headers={"User-Agent": "MyContract/1.0"}
    )
    
    data = fetcher.json(resp, "example-api")
    return {"result": data}
```

### Multi-source Fallback

```python
from web_fetcher import WebFetcher

def leader():
    fetcher = WebFetcher()
    
    # Try multiple sources
    sources = [
        "https://api1.example.com/data",
        "https://api2.example.com/data",
        "https://api3.example.com/data",
    ]
    
    for source in sources:
        try:
            resp = fetcher.get(source)
            if resp.status == 200:
                data = fetcher.json(resp, source)
                return {"data": data, "source": source}
        except gl.vm.UserError:
            continue  # Try next source
    
    raise gl.vm.UserError("All sources failed")
```

### Using Pre-built Patterns

```python
from web_fetcher import PriceFeedPattern

def leader():
    pattern = PriceFeedPattern()
    
    # Get ETH price with automatic fallback
    price_data = pattern.get_price(
        symbol="ETH",
        binance_hosts=[
            "https://api.binance.com",
            "https://api-gcp.binance.com",
        ],
        coingecko_fallback=True
    )
    
    return {
        "price": str(price_data["price"]),
        "source": price_data["source"]
    }
```

## API Reference

### WebFetcher

Core fetcher class with utility methods.

#### Methods

- `get(url, headers=None) -> Response`: Make GET request
- `json(resp, name) -> dict`: Parse JSON response with error handling
- `text(resp, name) -> str`: Get text response with error handling
- `ensure_status(resp, expected_status=200) -> Response`: Validate HTTP status

### PriceFeedPattern

Pre-built pattern for cryptocurrency price feeds.

#### Methods

- `get_price(symbol, binance_hosts, coingecko_fallback=True) -> dict`: Get price with fallback

### WeatherPattern

Pre-built pattern for weather data.

#### Methods

- `get_weather(lat, lon, name="weather") -> dict`: Get weather data

### NewsPattern

Pre-built pattern for news feeds.

#### Methods

- `get_news(source_urls, limit=10) -> list`: Get news items from multiple sources

## Examples

See `examples/` directory for complete contract examples.

## License

MIT

