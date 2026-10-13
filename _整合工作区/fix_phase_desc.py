import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 找到 do_produce 里 tpl = compose_prompt 那行
OLD = '''    input_text = input_text.replace("<你的名字>", app["key"])
    tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    note = format_note(program, phase_cfg)'''

NEW = '''    input_text = input_text.replace("<你的名字>", app["key"])
    # 关键：把「本环节任务说明」放在模板前面，让 AI 先知道要做什么
    _phase_desc = (phase_cfg.get("desc") or "").strip()
    _phase_name = phase_cfg.get("name") or phase_cfg.get("key") or ""
    _phase_header = ""
    if _phase_desc:
        _phase_header = (
            f"# 本环节：{_phase_name}\\n\\n"
            f"## 本环节任务说明\\n{_phase_desc}\\n\\n"
            f"## 以下是通用写作要求\\n\\n"
        )
    tpl = _phase_header + compose_prompt("PROMPT_PRODUCE.md", program)
    note = format_note(program, phase_cfg)'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_phase_desc")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已把「本环节任务说明」注入 prompt")
else:
    print("[FAIL] 找不到锚点")
    # 看看附近代码
    i = text.find('tpl = compose_prompt')
    if i >= 0:
        print("\n附近代码：")
        print(text[max(0,i-300):i+300])
