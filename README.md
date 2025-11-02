# GenLayer Oracle - Tools & Infrastructure

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GenLayer](https://img.shields.io/badge/GenLayer-Studionet-blue)](https://genlayer.com)

This project provides **reusable tools and libraries** for building GenLayer applications, plus **research contributions** for protocol improvements.

**Focus Areas**:
- 🛠️ **Tools & Infrastructure**: Reusable libraries for GenVM contracts
- 🔬 **Research & Analysis**: Performance benchmarks, security audits, protocol proposals

## What's Inside

This repository contains:

1. **Reference Oracle Contract** (`contracts/`) - Complete oracle implementation
2. **GenVM Web Fetcher Library** (`packages/genvm-web-fetcher/`) - Reusable web fetching utilities
3. **Oracle SDK** (`packages/oracle-sdk/`) - TypeScript SDK for oracle interactions
4. **API Key Management Patterns** (`docs/API_KEY_MANAGEMENT_PATTERNS.md`) - Secure API key handling patterns
5. **Research Plans** (`docs/RESEARCH_PLAN.md`) - Performance benchmarks, security analysis, protocol proposals

## 🏗️ Architecture

```
genlayer-oracle/
├── packages/           # Reusable Tools & Libraries
│   ├── genvm-web-fetcher/  # Python library for web fetching
│   └── oracle-sdk/         # TypeScript SDK for oracle contracts
├── contracts/          # GenVM Python contracts (reference/examples)
│   └── oracle_consumer.py
├── frontend/           # React + Vite dApp (optional demo)
├── src/                # Node.js demo/scripts (optional)
└── docs/               # Documentation & Research Plans
```

### Components

1. **OracleContract** (`contracts/oracle_consumer.py`)
   - Fetches data via `gl.nondet.web.get()` (non-deterministic)
   - Uses `gl.vm.run_nondet(leader, validator)` for consensus
   - Persists data on-chain
   - Emits `OracleUpdateEvent` on successful updates

2. **Frontend** (`frontend/`)
   - React + TypeScript + Vite
   - Integrates with `genlayer-js` SDK
   - Displays oracle data from contract

3. **Node Demo** (`src/`)
   - Example usage of `genlayer-js` SDK
   - Can be used for scripts/bots

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+ (for GenVM contract development and scripts)
- GenLayer runtime/network access

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

### Development

**1. Run Node.js demo (off-chain API clients):**
```bash
npm run dev
```

**2. Run Python client (interact with contracts):**
```bash
# Read from Oracle Consumer
python scripts/oracle_client.py 0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147

# Read from Simple Price Feed
python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888

# Update Simple Price Feed (write transaction)
python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888 update
```

**3. Build Node.js demo:**
```bash
npm run build
npm start
```

**4. Run Frontend dApp:**
```bash
cd frontend
npm run dev
```

## 📋 Contract Usage

### Deploy Contract

Deploy `contracts/oracle_consumer.py` to GenLayer network.

### Methods

**Write Methods:**
- `update_all(city: str, lat: str, lon: str, news_limit: int)` - Fetch and update all oracle data
  - Uses non-deterministic execution with validator consensus
  - Emits `OracleUpdateEvent` on success

**View Methods:**
- `get_status() -> dict` - Get current oracle data (price, weather, news)
- `debug_state() -> dict` - Debug method to check state persistence

### Events

- `OracleUpdateEvent(price, source, temperature, city, news_count)` - Emitted when data is updated

## 📦 Data Sources

- **Price**: Binance (6 mirrors) → Coingecko fallback
- **Weather**: Open-Meteo API
- **News**: Reddit → CoinDesk RSS fallback

## 🔧 Configuration

- **Chain**: Uses `studionet` (GenLayer Studio Network)
- TypeScript: `moduleResolution: "bundler"` for subpath exports
- Contract: Uses `genlayer.gl` for GenVM functionality
- All API calls include proper error handling and fallbacks

## 📝 Notes

- Contract state persists on-chain after successful `update_all()` calls
- Non-deterministic execution requires validator consensus
- All float values are encoded as strings for calldata compatibility

## 📚 Additional Resources

- [API Key Management Patterns](docs/API_KEY_MANAGEMENT_PATTERNS.md) - Secure patterns for handling API keys
- [Contribution Guidelines](CONTRIBUTING.md) - How to contribute to this project
- [Changelog](CHANGELOG.md) - Version history and changes
- [Research Plans](docs/RESEARCH_PLAN.md) - Performance and security research

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
