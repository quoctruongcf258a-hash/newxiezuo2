from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

print("=== 所有含「产出校验」的行 ===")
for i, ln in enumerate(lines):
    if "产出校验" in ln:
        print(f"  {i+1:4d}| {ln.strip()}")

print("\n=== 所有含「期望」+「落盘」的行 ===")
for i, ln in enumerate(lines):
    if "期望" in ln and "落盘" in ln:
        print(f"  {i+1:4d}| {ln.strip()}")
        # 打印上下文
        for j in range(max(0, i-15), min(len(lines), i+5)):
            print(f"    {j+1:4d}| {lines[j]}")
        print("  " + "-"*40)
