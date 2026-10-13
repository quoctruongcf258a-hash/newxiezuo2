from pathlib import Path

log = Path(r"F:\赛马23环整合工作室\_整合工作区\p09_log.txt")
text = log.read_text(encoding="utf-16", errors="replace")
lines = text.splitlines()

print(f"共 {len(lines)} 行")
print("=" * 70)
print("=== 前 50 行 ===")
for i, ln in enumerate(lines[:50], 1):
    print(f"  {i:3d}| {ln}")

print()
print("=" * 70)
print("=== 后 50 行 ===")
for i, ln in enumerate(lines[-50:], len(lines)-49):
    print(f"  {i:3d}| {ln}")
