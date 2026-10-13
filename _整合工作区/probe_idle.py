# probe_idle.py — 看 mix_send.py 里现有的相关函数
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = P.read_text(encoding="utf-8")
lines = text.splitlines()

print("=== 所有函数定义 ===")
for i, ln in enumerate(lines, 1):
    s = ln.lstrip()
    if s.startswith("def "):
        print(f"{i:4d}| {ln}")

print()
print("=== 含 wait / idle / busy / check 的行 ===")
for i, ln in enumerate(lines, 1):
    if any(k in ln.lower() for k in ["wait_", "_busy", "_idle", "check_running"]):
        print(f"{i:4d}| {ln[:130]}")