from pathlib import Path
import re

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

# ── 1. 找所有 chunk 生成函数 ──
print("=== 所有 def *chunk* 函数 ===")
for i, ln in enumerate(lines):
    if re.match(r"^\s*def\s+\w*chunk\w*\s*\(", ln):
        print(f"  {i+1:4d}| {ln}")

# ── 2. 找 chunks 变量定义 ──
print("\n=== chunks 相关赋值 ===")
for i, ln in enumerate(lines):
    if re.search(r"chunks\s*=", ln) or re.search(r"chunk_list\s*=", ln):
        print(f"  {i+1:4d}| {ln.strip()}")

# ── 3. 找"第一卷"、"第X卷"相关生成逻辑 ──
print("\n=== 含'第'+卷 的行 ===")
for i, ln in enumerate(lines):
    if re.search(r"第.*卷|卷.*第", ln) and ("chunk" in ln.lower() or "label" in ln.lower() or "name" in ln.lower()):
        print(f"  {i+1:4d}| {ln.strip()}")

# ── 4. 直接找 phase chunk 生成的核心函数 ──
print("\n=== 含 'chunk_' 或 'chunks' 的 def 附近代码 ===")
for i, ln in enumerate(lines):
    if re.match(r"^\s*def\s+", ln) and any(k in ln for k in ["chunk", "segment", "block", "chapter"]):
        print(f"\n--- {i+1}: {ln.strip()} ---")
        for j in range(i, min(i+25, len(lines))):
            print(f"  {j+1:4d}| {lines[j]}")
