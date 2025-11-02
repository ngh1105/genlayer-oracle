# Next Phase Tasks - Tools & Infrastructure

## ✅ Completed Tasks

1. ✅ **GenVM Web Fetcher Library** - Core library with patterns
2. ✅ **Oracle SDK** - Complete TypeScript SDK with both contract types
3. ✅ **Deployed Contracts** - 2 working contracts on studionet
4. ✅ **Frontend Integration** - React app supporting both contracts
5. ✅ **Documentation** - Comprehensive guides and examples

## 🎯 Immediate Next Steps

### Priority 1: Expand Web Fetcher Library (50-500 pts)

**Add More Patterns**:

1. **Stock Price Pattern** 
   - Yahoo Finance API
   - Alpha Vantage API
   - Multi-source fallback

2. **Sports Scores Pattern**
   - TheSportsDB API
   - ESPN API (public endpoints)
   - Fallback handling

3. **Social Media Pattern** (enhance existing)
   - Twitter/X RSS
   - Reddit (improved)
   - Multiple feed aggregation

**Location**: `packages/genvm-web-fetcher/web_fetcher.py`

### Priority 2: API Key Management Patterns (200-500 pts)

**Goal**: Create secure patterns for handling API keys

**Approaches to Document**:
1. **Off-chain Proxy Pattern**
   - Contract → Proxy Service (holds keys) → API
   - Keys never touch blockchain

2. **Encrypted On-chain Pattern**
   - Encrypt keys, store on-chain
   - Decrypt in leader function (leader-only)

3. **Key Rotation Pattern**
   - Support for key rotation
   - Multiple key storage

**Deliverable**: `docs/API_KEY_MANAGEMENT_PATTERNS.md`

### Priority 3: Enhanced Documentation (100-300 pts)

1. **Repository Enhancements**:
   - Add LICENSE file (MIT)
   - Add CONTRIBUTING.md
   - Add badges to README
   - Add GitHub Actions (CI/CD)

2. **Usage Guides**:
   - Complete deployment guide
   - Integration examples
   - Best practices

### Priority 4: Developer Tools (200-800 pts)

1. **Contract Generator CLI**
   ```bash
   npx genvm-cli create oracle --template price-feed
   ```

2. **Deployment Automation**
   - Automated deployment scripts
   - Contract verification tools

3. **Testing Framework**
   - Mock nondet functions
   - State persistence testing

## 📊 Points Potential

**Current Completion**:
- ✅ Web Fetcher Library: ~200-500 pts (basic version)
- ✅ Oracle SDK: ~200-800 pts ✅ COMPLETE
- ✅ Deployed Contracts: Reference implementations

**Next Phase Potential**:
- More Patterns: +50-500 pts
- API Key Management: +200-500 pts
- Developer Tools: +200-800 pts
- Documentation: +100-300 pts

**Total Potential**: 750-3000+ pts 🎯

## Recommended Order

1. **API Key Management Patterns** (high value, quick to document)
2. **Add More Patterns** (extends existing library)
3. **Repository Enhancements** (makes project more professional)
4. **Developer Tools** (longer-term, higher complexity)

---

**Current Status**: Oracle SDK complete ✅

**Next Immediate Task**: API Key Management Patterns documentation

