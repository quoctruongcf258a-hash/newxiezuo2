from pathlib import Path
import re

# ── 1. 找 mix_send 模块 ──
print("=== 找 mix_send 相关文件 ===")
for p in Path(r"F:\赛马23环整合工作室").rglob("mix_send.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    print(f"  {p}")

# ── 2. 读 mix_send.py 里所有 def ──
print("\n=== mix_send 里所有函数 ===")
for p in Path(r"F:\赛马23环整合工作室").rglob("mix_send.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("def "):
            print(f"  {p.name}:{i+1}  {ln.strip()}")

# ── 3. 找 check_running 完整代码 ──
print("\n=== check_running 函数 ===")
for p in Path(r"F:\赛马23环整合工作室").rglob("mix_send.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    i_func = None
    for i, ln in enumerate(lines):
        if ln.startswith("def check_running"):
            i_func = i
            break
    if i_func is None:
        continue
    print(f"文件：{p}")
    for j in range(i_func, min(i_func + 60, len(lines))):
        print(f"  {j+1:4d}| {lines[j]}")

# ── 4. 全盘搜索"监控"或"busy"或"status"相关脚本 ──
print("\n=== 含 监控/busy/idle/status 的 .py（排除第三方）===")
for p in Path(r"F:\赛马23环整合工作室").rglob("*.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    name = p.name.lower()
    if any(k in name for k in ["monitor", "busy", "status", "idle", "watch", "check_busy"]):
        print(f"  {p.relative_to(Path(r'F:\赛马23环整合工作室'))}")

# ── 5. orchestrator.py 里所有调 check_running / capture 的地方 ──
print("\n=== orchestrator.py 里所有 check_running / capture 调用 ===")
orch = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
if orch.exists():
    lines = orch.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if "check_running" in ln or "capture_with_meta" in ln or "check_busy" in ln:
            print(f"  {i+1:4d}| {ln.strip()}")
