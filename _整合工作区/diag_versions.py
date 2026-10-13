from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

#  1. 看 _do_produce_batch 的返回段 
print("=== _do_produce_batch 的 out_files 构造段 ===")
for i, ln in enumerate(lines):
    if "out_files = []" in ln:
        for j in range(max(0, i-5), min(len(lines), i+15)):
            print(f"  {j+1:4d}| {lines[j]}")
        print("  " + "-"*50)

#  2. 看 dry 伪造块和校验块的完整顺序 
print("\n=== dry 伪造块 + 校验块的顺序 ===")
i_dry = None
i_check = None
for i, ln in enumerate(lines):
    if "dry-run 模式且没有产出时，先伪造 versions" in ln:
        i_dry = i
    if "汇总产出校验（目录式命名" in ln:
        i_check = i
if i_dry is not None and i_check is not None:
    print(f"  dry 伪造块在第 {i_dry+1} 行")
    print(f"  校验块在第 {i_check+1} 行")
    print(f"  顺序：{'正确 [OK]' if i_dry < i_check else '错误 [FAIL]'}")
    print("\n--- dry 伪造块全文 ---")
    for j in range(i_dry, i_check):
        print(f"  {j+1:4d}| {lines[j]}")
else:
    print(f"  i_dry={i_dry}, i_check={i_check}")
