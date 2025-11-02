# Giải Thích: Tại Sao Không Dùng genlayer-py?

## 🔍 Phân Biệt Quan Trọng

### Hiện Tại:

1. **Contracts (On-chain - GenVM)**:
   - Dùng: `import genlayer.gl as gl`
   - Dependency: `# { "Depends": "py-genlayer:latest" }`
   - **KHÔNG THỂ ĐỔI** - Đây là GenVM runtime

2. **Off-chain Scripts**:
   - TypeScript: Dùng `genlayer-js` ✅ (`src/index.ts`)
   - Python: **KHÔNG CÓ** ❌

---

## 💡 Vấn Đề

Hiện tại chỉ có TypeScript scripts để interact với contracts off-chain, **KHÔNG CÓ Python scripts**.

Điều này **KHÔNG ĐỦ** nếu muốn:
- Python developers có thể interact với contracts
- Parity giữa TypeScript và Python
- Complete Tools & Infrastructure (nên có cả 2 languages)

---

## ✅ Giải Pháp: Tạo Python Scripts Dùng genlayer-py

### Tạo Python Scripts Tương Tự TypeScript:

```python
# scripts/interact_contracts.py (NEW)
from genlayer_py import create_client, create_account, studionet

# Tương tự src/index.ts nhưng bằng Python
```

---

## 📊 So Sánh

| Use Case | TypeScript | Python | Status |
|----------|-----------|--------|--------|
| **On-chain Contracts** | N/A | `genlayer.gl` | ✅ Required |
| **Off-chain Scripts** | `genlayer-js` ✅ | ❌ Missing | **Cần thêm** |

---

## 🎯 Recommendation

### Nên Tạo Python Scripts Dùng genlayer-py:

1. **scripts/oracle_client.py** - Tương tự `src/index.ts`
   - Read contract status
   - Update contract
   - Off-chain API demo

2. **scripts/deploy_helper.py** - Deploy helper scripts
   - Deploy contracts
   - Set initial state

**Lợi ích**:
- ✅ Complete Python support
- ✅ Parity với TypeScript
- ✅ Better Tools & Infrastructure
- ✅ +50-200 pts

---

## 📝 Implementation Plan

### Task: Tạo Python Client Scripts

1. **Install genlayer-py**:
   ```bash
   pip install genlayer-py
   ```

2. **Create scripts/oracle_client.py**:
   - Similar to `src/index.ts`
   - Read contract using `genlayer-py`
   - Update contract using `genlayer-py`

3. **Update README**:
   - Document Python scripts usage
   - Show examples

---

**Conclusion**: Contracts PHẢI dùng `genlayer.gl`, nhưng nên TẠO THÊM Python scripts dùng `genlayer-py` cho off-chain interactions!

