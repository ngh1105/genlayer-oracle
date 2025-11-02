# Cleanup Recommendations

## Dependencies Analysis

### Packages Dependencies

1. **genvm-web-fetcher** (Python)
   - ✅ **KHÔNG cần** genlayer-js
   - ✅ Standalone Python library
   - ✅ **CÓ THỂ XÓA** genlayer-js nếu chỉ làm package này

2. **oracle-sdk** (TypeScript)
   - ❌ **CẦN** genlayer-js (imports from 'genlayer-js')
   - ❌ **KHÔNG THỂ XÓA** genlayer-js nếu giữ package này
   - **Option**: Dùng published npm package nếu có

### Contract Dependencies

- **oracle_consumer.py**
  - ✅ **KHÔNG cần** genlayer-js folder
  - ⚠️ Chỉ là **example/reference** nếu focus vào Tools
  - **CÓ THỂ XÓA** nếu không cần example

---

## Recommendation Based on Focus

### Option 1: **Pure Tools (GenVM Web Fetcher only)** ✅ Recommended

**If chỉ focus vào genvm-web-fetcher**:

**KEEP**:
- ✅ `packages/genvm-web-fetcher/`
- ✅ `docs/` (research plans)

**DELETE**:
- ❌ `genlayer-js/` folder (không cần)
- ❌ `contracts/` (không cần example nếu chỉ làm library)
- ❌ `packages/oracle-sdk/` (cần genlayer-js)
- ❌ `frontend/` (không cần demo)
- ❌ `src/` (không cần demo)

**Result**: Clean, focused repository cho Tools contribution

---

### Option 2: **Tools + SDK (Cần genlayer-js)**

**If muốn giữ cả web-fetcher và oracle-sdk**:

**KEEP**:
- ✅ `packages/genvm-web-fetcher/`
- ✅ `packages/oracle-sdk/`
- ✅ `genlayer-js/` (required dependency)
- ✅ `docs/`

**DELETE** (optional):
- ❌ `contracts/` (có thể xóa nếu không cần reference)
- ❌ `frontend/` (có thể xóa nếu không cần demo)
- ❌ `src/` (có thể xóa nếu không cần demo)

**Result**: Tools repository với cả Python và TypeScript libraries

---

### Option 3: **Tools + Research Only**

**If chỉ làm Tools và Research, không cần SDK**:

**KEEP**:
- ✅ `packages/genvm-web-fetcher/`
- ✅ `docs/` (research plans)

**DELETE**:
- ❌ `genlayer-js/` (không cần)
- ❌ `packages/oracle-sdk/` (cần genlayer-js)
- ❌ `contracts/` (không cần example)
- ❌ `frontend/` (không cần demo)
- ❌ `src/` (không cần demo)

**Result**: Minimal, focused repository

---

## My Recommendation: **Option 1**

Vì bạn focus vào **Tools & Infrastructure**:

1. **Giữ**: `packages/genvm-web-fetcher/` - Standalone, không cần genlayer-js
2. **Xóa**: 
   - `genlayer-js/` - Không cần nếu chỉ làm Python library
   - `packages/oracle-sdk/` - Cần genlayer-js, có thể làm sau nếu cần
   - `contracts/` - Không cần example nếu chỉ làm library
   - `frontend/` - Không cần demo
   - `src/` - Không cần demo

**Clean structure**:
```
genlayer-oracle/
├── packages/
│   └── genvm-web-fetcher/
├── docs/
│   └── RESEARCH_PLAN.md
└── README.md
```

**Points**: 200-500 pts (từ genvm-web-fetcher) + research points

---

## Alternative: Nếu muốn giữ oracle-sdk

Thì phải giữ genlayer-js, nhưng có thể:
- Chuyển oracle-sdk sang dùng published npm package (nếu có)
- Hoặc giữ genlayer-js như dependency

**Bạn muốn focus vào gì?**
- A) Chỉ genvm-web-fetcher → Xóa hết, giữ library
- B) Cả web-fetcher + SDK → Giữ genlayer-js
- C) Web-fetcher + Research → Xóa genlayer-js, giữ library + research

