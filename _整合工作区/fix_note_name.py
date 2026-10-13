# fix_note_name.py — 把 PROMPT_PRODUCE.md 里的「本次补强要求」改为「输出格式要求」
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\prompts\PROMPT_PRODUCE.md")

text = TARGET.read_text(encoding="utf-8")

old = "- 【本次补强要求】——上一轮终审的反对意见，必须逐条对应处理；"
new = "- 【输出格式要求】——严格按下方【输出格式要求】小节执行；"

if old not in text:
    print("没找到目标行，可能已改过或格式不同")
else:
    bak = TARGET.with_suffix(".md.bak_note")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    text = text.replace(old, new)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改名为『输出格式要求』")