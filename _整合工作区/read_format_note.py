from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

# 找 format_note 函数
found = False
for i, ln in enumerate(lines):
    if ln.startswith("def format_note"):
        found = True
        print(f"=== def format_note 位于第 {i+1} 行 ===\n")
        end = i + 1
        while end < len(lines) and end < i + 250:
            if end > i + 1 and lines[end].startswith("def "):
                break
            end += 1
        for j in range(i, end):
            print(f"{j+1:4d}| {lines[j]}")
        print(f"\n=== 函数总长度: {end - i} 行 ===")
        break

if not found:
    print("❌ 找不到 def format_note")
