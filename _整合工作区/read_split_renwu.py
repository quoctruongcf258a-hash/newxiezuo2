from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

# ── 1. 找 def _split_renwu ──
found = False
for i, ln in enumerate(lines):
    if "_split_renwu" in ln and ln.strip().startswith("def "):
        found = True
        print(f"=== def _split_renwu 位于第 {i+1} 行 ===\n")
        end = i + 1
        while end < len(lines) and end < i + 150:
            if end > i + 1 and lines[end].startswith("def "):
                break
            end += 1
        for j in range(i, end):
            print(f"{j+1:4d}| {lines[j]}")
        print(f"\n=== 函数长度：{end - i} 行 ===")
        break

if not found:
    print("❌ 找不到 def _split_renwu")

# ── 2. 找所有调用点 ──
print("\n=== 所有 _split_renwu 调用点 ===")
for i, ln in enumerate(lines):
    if "_split_renwu" in ln and not ln.strip().startswith("def "):
        print(f"  {i+1:4d}| {ln.strip()}")
