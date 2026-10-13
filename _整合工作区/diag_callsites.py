from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 找 _run_task_stage 和 _do_produce_batch 里的 _judge_task_status 调用点
for fn_name in ["_run_task_stage", "_do_produce_batch"]:
    m = re.search(rf"def {fn_name}\(.*?(?=\n\ndef |\n\n# |\Z)", text, re.DOTALL)
    if not m:
        print(f"❌ 找不到 {fn_name}")
        continue
    body = m.group(0)
    print(f"\n{'='*70}")
    print(f"=== {fn_name} ===")
    print('='*70)
    # 找 _judge_task_status 出现的行，打印周围 20 行
    lines = body.splitlines()
    for i, ln in enumerate(lines):
        if "_judge_task_status" in ln:
            start = max(0, i - 15)
            end = min(len(lines), i + 8)
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j+1:4d}| {lines[j]}")
            print("  " + "-"*60)
