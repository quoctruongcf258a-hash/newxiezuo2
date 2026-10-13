import shutil
import re
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_dynamic_step")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 用正则匹配 _file_mode_task 里的 return 段（松散匹配）
pattern = re.compile(
    r'    _ai = app\.get\("key"\) or "unknown"\n'
    r'    # 步骤显示.*?\n'
    r'    if total_steps and stage_end:.*?'
    r'    \)\n',
    re.DOTALL,
)

NEW = '''    _ai = app.get("key") or "unknown"
    # 动态步骤号：按 out_path 分配（重发复用，新任务 +1）
    try:
        from orchestrator import _get_or_assign_step
        _task_key = str(out_path).replace("\\\\", "/")
        _step_no = _get_or_assign_step(_ai, _task_key)
    except Exception as e:
        print(f"   [step] 分配失败：{e}")
        _step_no = 1

    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"最后**必须**回复这一行（一字不改）：\\n"
        f"  ✅ [{_ai}] {phase_label} → 步骤{_step_no} 已完成\\n"
        f"不要输出多余说明。"
    )
'''

m = pattern.search(text)
if m:
    text = text[:m.start()] + NEW + text[m.end():]
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已替换 _file_mode_task 的 return 段")
else:
    print("[FAIL] 正则没匹配到")
    print("附近代码（_file_mode_task 里 _ai = 开始）：")
    i = text.find('    _ai = app.get("key") or "unknown"')
    if i >= 0:
        print(text[i:i+900])
