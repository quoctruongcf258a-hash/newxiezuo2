from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

print("=== 所有提到「人物」/「renwu」/「人物设计列表」的行 ===")
for i, ln in enumerate(lines):
    if any(k in ln for k in ["人物设计列表", "人物设计", "renwu", "_split_renwu", "person_list"]):
        print(f"  {i+1:4d}| {ln}")

print("\n=== 定位 _do_produce 函数（产出主流程）===")
for i, ln in enumerate(lines):
    if ln.strip().startswith("def _do_produce") or ln.strip().startswith("def _produce"):
        print(f"\n=== 第 {i+1} 行：{ln.strip()} ===")
        # 打印函数前 60 行
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1:4d}| {lines[j]}")
        break
