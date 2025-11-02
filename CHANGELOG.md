# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- API Key Management Patterns documentation
- Three API key management pattern implementations (Off-chain Proxy, Encrypted On-chain, Key Rotation)
- Proxy service example (Node.js)
- Key encryption script (Python)
- Enhanced project documentation

## [1.0.0] - 2025-11-02

### Added
- **GenVM Web Fetcher Library** (`packages/genvm-web-fetcher/`)
  - Core `WebFetcher` class with utility methods
  - Pre-built patterns: `PriceFeedPattern`, `WeatherPattern`, `NewsPattern`
  - Multi-source fallback mechanism
  - Error handling with `gl.vm.UserError`
  - Comprehensive documentation and examples

- **Oracle SDK** (`packages/oracle-sdk/`)
  - `OracleSDK` for Oracle Consumer contracts
  - `SimplePriceFeedSDK` for Simple Price Feed contracts
  - Event subscriptions with polling
  - Transaction finalization helpers
  - Type-safe TypeScript interfaces
  - Usage examples

- **Deployed Contracts**
  - Simple Price Feed contract (`0xe328378CAF086ae0a6458395C9919a4137fCb888`)
  - Oracle Consumer contract (`0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`)
  - Both contracts deployed and tested on `studionet`
  - State persistence verified

- **Frontend Integration** (`frontend/`)
  - React + Vite application
  - Support for both contract types
  - Auto-fill contract addresses
  - Real-time data reading
  - Transaction sending with status tracking

- **Documentation**
  - Comprehensive README files
  - API documentation
  - Deployment guides
  - Troubleshooting guides
  - Research plans
  - Contribution roadmap

### Fixed
- State persistence in contracts (type annotations in class body)
- Float encoding issues (converted to strings for calldata)
- Import path issues with `genlayer-js` subpath exports
- Type errors in TypeScript SDK

### Changed
- Updated to use `studionet` instead of `localnet`
- Migrated from local `genlayer-js` folder to npm package
- Improved error handling in contracts

### Technical Details
- Contracts use proper state persistence patterns
- SDK uses polling for event subscriptions
- Frontend supports multiple contract types dynamically
- All examples tested and verified

---

## Version History

### [1.0.0] - 2025-11-02
**Initial Release**
- Complete Tools & Infrastructure implementation
- Production-ready libraries and SDKs
- Deployed and tested contracts
- Comprehensive documentation

---

## Legend

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Features that will be removed
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security updates

