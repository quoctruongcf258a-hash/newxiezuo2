# fix_placeholder.py — do_produce 里把 <你的名字> 替换成实际 key
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    """① 产出：一名 AI 产出一版。"""
    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"
    label = f"{program} › {phase_cfg['key']}"
    tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    note = format_note(program, phase_cfg)
'''

NEW = '''    """① 产出：一名 AI 产出一版。"""
    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"
    label = f"{program} › {phase_cfg['key']}"
    # 把输入材料里的 <你的名字> 替换成实际 AI key
    input_text = input_text.replace("<你的名字>", app["key"])
    tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    note = format_note(program, phase_cfg)
'''

text = TARGET.read_text(encoding="utf-8")

if "input_text.replace(\"<你的名字>\"" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_placeholder")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已加 <你的名字> 替换")