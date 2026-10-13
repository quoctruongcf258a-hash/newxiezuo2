import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 各种可能的调用形式
patterns = [
    ("status = _judge_task_status(ai_key, _vf, t_wait) if not dry else \"success\"",
     "status = _wait_ai_task_done(ai_key, _vf, max_wait_sec=t_wait, min_startup_sec=30) if not dry else \"success\""),
    ("status = _judge_task_status(ai_key, _vf, t_wait)",
     "status = _wait_ai_task_done(ai_key, _vf, max_wait_sec=t_wait, min_startup_sec=30)"),
    ("status = _judge_task_status(_k, _vf, t_wait)",
     "status = _wait_ai_task_done(_k, _vf, max_wait_sec=t_wait, min_startup_sec=30)"),
]

changed = 0
for old, new in patterns:
    cnt = text.count(old)
    if cnt > 0:
        text = text.replace(old, new)
        print(f"[OK] 替换 {cnt} 处：{old[:60]}...")
        changed += cnt

if changed > 0:
    bak = TARGET.with_suffix(".py.bak_replace")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 共替换 {changed} 处")
else:
    print("[FAIL] 找不到任何调用点")
