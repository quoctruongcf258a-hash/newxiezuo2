import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    # ── 润色阶段（读 02_写作/W3_正文 的同章产出）──
    "R1_润色":          ("02_写作/W3_正文", "current_stage_split"),'''

NEW = '''    # ── 润色阶段（读 01_规划/粗纲规划 的章列表，按当前阶段过滤）──
    "R1_润色":          ("01_规划/粗纲规划", "current_stage_split"),'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_r1_source")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已修复：R1_润色 改为读 P15 章列表")
else:
    print("[FAIL] 找不到锚点")
