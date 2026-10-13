# probe_mixsend2.py — 看 mix_send.send 的实现 + 重试逻辑
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "文件总行数", "=" * 30)
print(len(lines), "行")

print()
print("=" * 30, "所有 def / class", "=" * 30)
for i, ln in enumerate(lines, 1):
    s = ln.lstrip()
    if s.startswith("def ") or s.startswith("class "):
        print(f"{i:4d}| {ln[:120]}")

print()
print("=" * 30, "含 retry / 重发 / timeout / Connection / 失败", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["retry", "重发", "重试", "timeout", "Connection",
                              "失败", "attempt", "for _ in range", "sleep"]):
        print(f"{i:4d}| {ln[:140]}")