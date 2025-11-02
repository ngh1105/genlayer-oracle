# Project Structure

GenLayer Oracle - Tools & Infrastructure + Research Project

## Current Structure

```
genlayer-oracle/
├── contracts/                  # GenVM Python Contracts
│   ├── oracle_consumer.py      # Main oracle contract (reference implementation)
│   └── README.md
│
├── packages/                    # Reusable Tools & Libraries
│   ├── genvm-web-fetcher/      # ✅ Web Fetcher Library (Category 2)
│   │   ├── web_fetcher.py
│   │   ├── examples/
│   │   └── README.md
│   │
│   └── oracle-sdk/             # ✅ Oracle SDK (Category 2)
│       ├── src/
│       │   └── OracleSDK.ts
│       └── README.md
│
├── frontend/                    # React dApp (demo)
│   └── src/
│       └── App.tsx              # UI for oracle interaction
│
├── src/                         # Node.js Demos
│   └── index.ts                 # Demo script
│
├── docs/                        # Documentation & Plans
│   ├── CONTRIBUTION_ROADMAP.md
│   ├── TOOLS_IMPLEMENTATION_PLAN.md
│   ├── RESEARCH_PLAN.md
│   └── api-vs-contract.md
│
├── genlayer-js/                 # Local GenLayer SDK (reference)
│   └── ...
│
└── README.md                    # Main project README
```

## What's Good

✅ **Contracts**: Oracle contract hoàn chỉnh  
✅ **Packages**: Tools đã được tách thành packages riêng  
✅ **Docs**: Documentation đầy đủ  
✅ **Frontend**: Demo UI sẵn có  

## Suggested Improvements (Optional)

### 1. Add Workspace Configuration
Nếu muốn manage packages như monorepo:

```json
// package.json (root)
{
  "workspaces": [
    "packages/*"
  ]
}
```

### 2. Research Directory
Tạo folder cho research outputs:

```
research/
├── benchmarks/
│   └── performance-report.md
├── security/
│   └── audit-report.md
└── proposals/
    └── enhancement-proposals/
```

### 3. Examples Directory
Tập trung examples:

```
examples/
├── contracts/           # Example contracts using web-fetcher
├── frontend/            # Example frontend integrations
└── scripts/             # Example scripts
```

## Recommendation

**KHÔNG CẦN XÓA VÀ TẠO LẠI** ✅

**Chỉ cần**:
1. ✅ Giữ nguyên structure hiện tại
2. ✅ Continue building trong packages/
3. ✅ Add research outputs khi làm research
4. ✅ Update README để reflect focus vào Tools & Research

**Cấu trúc hiện tại đã phù hợp cho**:
- Tools & Infrastructure contributions
- Research & Analysis
- Example implementations

Chỉ cần tiếp tục develop trong structure hiện tại!

