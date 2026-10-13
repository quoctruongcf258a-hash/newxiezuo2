# probe_cdp.py — 找 CDP 发送 / 重发 相关逻辑
from pathlib import Path

SCRATCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

# 找所有含 CDP 的 py 文件
print("=" * 30, "含 CDP 的文件", "=" * 30)
for p in SCRATCH.glob("*.py"):
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
        if "CDP" in t or "cdp" in t:
            n = t.count("CDP") + t.count("cdp")
            print(f"  {p.name}  ({n} 处)")
    except Exception:
        pass

# 找 orchestrator.py 里调用 CDP 的地方
print()
print("=" * 30, "orchestrator.py 里 CDP 相关行", "=" * 30)
O = SCRATCH / "orchestrator.py"
lines = O.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["CDP", "cdp", "mix_send", "重发", "retry", "timeout", "Connection timed"]):
        print(f"{i:4d}| {ln[:140]}")

# 找 session.py / mix_send.py
print()
print("=" * 30, "session.py / mix_send.py 里的 send 相关", "=" * 30)
for name in ["session.py", "mix_send.py"]:
    p = SCRATCH / name
    if not p.exists():
        print(f"  {name}: 不存在")
        continue
    print(f"\n--- {name} ---")
    ls = p.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(ls, 1):
        if any(k in ln for k in ["def send", "retry", "重发", "for _", "range(",
                                  "timeout", "CDP", "except", "raise"]):
            print(f"{i:4d}| {ln[:140]}")