# GenLayer Oracle

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GenLayer](https://img.shields.io/badge/GenLayer-Studionet-blue)](https://genlayer.com)

This project provides **reusable tools and libraries** for building GenLayer oracle applications.

## What's Inside

This repository contains:

1. **GenVM Web Fetcher Library** (`packages/genvm-web-fetcher/`) - Reusable Python library for web fetching in GenVM contracts
2. **Oracle SDK** (`packages/oracle-sdk/`) - TypeScript SDK for oracle contract interactions
3. **Deployed Contracts** - Production-ready oracle contracts on studionet
4. **API Key Management Patterns** (`docs/API_KEY_MANAGEMENT_PATTERNS.md`) - Secure API key handling patterns
5. **Python Client Script** (`scripts/oracle_client.py`) - Off-chain Python client using genlayer-py SDK
6. **Frontend dApp** (`frontend/`) - React + TypeScript demo application

## 🏗️ Architecture

```
genlayer-oracle/
├── packages/                    # Libraries
│   ├── genvm-web-fetcher/      # Python library for web fetching
│   │   ├── web_fetcher.py      # Core WebFetcher class
│   │   └── DEPLOY_READY/       # Production-ready examples
│   └── oracle-sdk/             # TypeScript SDK
│       ├── src/
│       │   ├── OracleSDK.ts    # Full oracle SDK
│       │   ├── SimplePriceFeedSDK.ts
│       │   └── index.ts
│       └── examples/           # Usage examples
│
├── contracts/                   # GenVM Python Contracts
│   ├── oracle_consumer.py      # ✅ DEPLOYED - Full oracle
│   ├── api-key-patterns/        # Pattern examples
│   └── simple_price_feed_complete.py  # ✅ DEPLOYED - Simple price feed
│
├── frontend/                    # React + Vite dApp
│   └── src/App.tsx             # Supports both deployed contracts
│
├── scripts/                     # Utility scripts
│   └── oracle_client.py         # Python client (genlayer-py)
│
├── src/                         # Node.js demo/scripts
│   └── index.ts                # TypeScript client demo
│
└── docs/                        # Documentation
    └── API_KEY_MANAGEMENT_PATTERNS.md
```

## ✅ Deployed Contracts

### 1. Simple Price Feed
- **Contract Address**: `0xe328378CAF086ae0a6458395C9919a4137fCb888`
- **Network**: studionet (GenLayer Studio Network)
- **Status**: ✅ Deployed and Working
- **Methods**:
  - `get_price() -> dict`: Returns `{"price": str, "source": str}`
  - `update_price() -> None`: Fetches and stores ETH price
  - `debug_state() -> dict`: Debug state information

### 2. Oracle Consumer (Full Oracle)
- **Contract Address**: `0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`
- **Network**: studionet (GenLayer Studio Network)
- **Status**: ✅ Deployed and Working
- **Methods**:
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

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+ (for GenVM contract development)
- Python 3.12+ (required for genlayer-py SDK and Python client scripts)
- GenLayer runtime/network access

**Note**: The Python client script (`scripts/oracle_client.py`) requires **Python 3.12+** due to genlayer-py SDK dependencies.
- ✅ **Recommended**: Python 3.12 (has pre-built wheels for all dependencies)
- ⚠️ **Python 3.14**: May require Visual Studio Build Tools for `ckzg` dependency
- For Python <3.12, use the TypeScript client (`src/index.ts`) instead.

### Installation

```bash
# Install root dependencies
npm install

# Install Python dependencies (for off-chain scripts)
pip install -r requirements.txt

# Install frontend dependencies (if using frontend)
cd frontend && npm install

# Install package dependencies (if developing packages)
cd packages/oracle-sdk && npm install
```

### Usage

#### 1. Run Node.js Demo (TypeScript Client)

```bash
npm run dev
```

Or build and run:
```bash
npm run build
npm start
```

#### 2. Run Python Client

```bash
# On Windows with Python 3.12:
py -3.12 scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888

# Or if Python 3.12+ is your default:
python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888

# Read from Oracle Consumer
python scripts/oracle_client.py 0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147

# Update Simple Price Feed (write transaction)
python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888 update
```

#### 3. Run Frontend dApp

```bash
cd frontend
npm run dev
```

The frontend supports both deployed contracts:
- Switch between "Simple Price Feed" and "Oracle Consumer" using dropdown
- Contract addresses are auto-filled
- Real-time data reading and transaction sending

## 📋 Contract Usage

### Using TypeScript SDK

```typescript
import { createClient, createAccount } from 'genlayer-js'
import { studionet } from 'genlayer-js/chains'
import { SimplePriceFeedSDK } from '@genlayer-oracle/oracle-sdk'

const account = createAccount()
const client = createClient({ chain: studionet, account })

const sdk = new SimplePriceFeedSDK(
  client,
  '0xe328378CAF086ae0a6458395C9919a4137fCb888'
)

// Read price
const price = await sdk.getPrice()
console.log(`Price: $${price.price} from ${price.source}`)

// Update price
await sdk.updatePriceAndWait()
```

### Using Python Client

```python
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet

account = create_account()
client = create_client(chain=studionet, account=account)

# Read from contract
result = client.read_contract(
    address='0xe328378CAF086ae0a6458395C9919a4137fCb888',
    function_name='get_price',
    args=[],
)
print(f"Price: ${result['price']} from {result['source']}")
```

## 📦 Data Sources

- **Price**: Binance (6 mirrors) → Coingecko fallback
- **Weather**: Open-Meteo API
- **News**: Reddit → CoinDesk RSS fallback

## 🛠️ Components

### GenVM Web Fetcher Library

Reusable Python library for fetching web data in GenVM contracts.

**Features**:
- Core `WebFetcher` class with utilities
- Pre-built patterns: `PriceFeedPattern`, `WeatherPattern`, `NewsPattern`
- Multi-source fallback mechanism
- Error handling with `gl.vm.UserError`

**Location**: `packages/genvm-web-fetcher/web_fetcher.py`

### Oracle SDK

TypeScript SDK for interacting with oracle contracts.

**Features**:
- `OracleSDK` for Oracle Consumer contracts
- `SimplePriceFeedSDK` for Simple Price Feed contracts
- Event subscriptions with polling
- Transaction finalization helpers
- Type-safe TypeScript interfaces

**Location**: `packages/oracle-sdk/`

### Python Client

Off-chain Python script using genlayer-py SDK.

**Features**:
- Read from deployed contracts
- Send write transactions
- Auto-detect contract type
- Support for both Simple Price Feed and Oracle Consumer

**Location**: `scripts/oracle_client.py`

## 🔧 Configuration

- **Chain**: Uses `studionet` (GenLayer Studio Network)
- TypeScript: `moduleResolution: "bundler"` for subpath exports
- Contract: Uses `genlayer.gl` for GenVM functionality
- All API calls include proper error handling and fallbacks

## 📝 Key Learnings

1. **State Persistence**: Fields MUST be declared in class body with type annotations
2. **Type Restrictions**: Can't use plain `int`, use `str`, `float`, `bigint`, or sized integers
3. **Non-deterministic Execution**: Uses `gl.vm.run_nondet(leader, validator)` for consensus
4. **Multi-source Fallback**: Essential for reliability (Binance mirrors → Coingecko)

## 📚 Additional Resources

- [API Key Management Patterns](docs/API_KEY_MANAGEMENT_PATTERNS.md) - Secure patterns for handling API keys
- [Changelog](CHANGELOG.md) - Version history and changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/ngh1105/genlayer-oracle.git
- **Network**: studionet (GenLayer Studio Network)
- **GenLayer Docs**: https://docs.genlayer.com
