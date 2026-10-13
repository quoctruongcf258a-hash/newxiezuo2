import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_step_call")
if not bak.exists():
    shutil.copy(bak, bak)
    print(f"已备份：{bak.name}")

# ── 在 _do_produce_batch 里，把 total_steps / stage_end 传给 build_produce_task ──
# 找到 build_produce_task 的调用

import re
m = re.search(r"def _do_produce_batch\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    # 找 build_task 定义
    i = body.find("def build_task")
    if i >= 0:
        print("=" * 70)
        print("当前 build_task：")
        print("=" * 70)
        print(body[i:i+600])
