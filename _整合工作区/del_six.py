# del_six.py — 删 PROMPT_PRODUCE.md 里的「六要素对齐」这一条
import re
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\prompts\PROMPT_PRODUCE.md")

text = TARGET.read_text(encoding="utf-8")

if "六要素对齐" not in text:
    print("已经没有『六要素对齐』，不用改")
else:
    bak = TARGET.with_suffix(".md.bak_six")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 删掉「3. **六要素对齐**：...」这一整条（含缩进的后续行）
    text2 = re.sub(
        r"3\. \*\*六要素对齐\*\*：[^\n]*\n(?:   [^\n]*\n)*",
        "",
        text
    )

    # 重编号：4→3, 5→4, 6→5
    text2 = text2.replace("4. **语言**", "3. **语言**")
    text2 = text2.replace("5. **不做这三件事**", "4. **不做这三件事**")
    text2 = text2.replace("6. **不回头**", "5. **不回头**")

    TARGET.write_text(text2, encoding="utf-8")
    print("✔ 已删『六要素对齐』并重编号")