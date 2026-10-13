# fix_send_final.py — 撤回 QUEST 的 Ctrl+Enter，统一用纯 Enter
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

# 找到当前的发送块（可能是 fix_send_wait 的版本或 fix_quest_send 的版本）
OLD = '''        _mods = 2 if ai == "QUEST" else 0
'''

NEW = '''        _mods = 0   # 全部用纯 Enter（QUEST 实测 Enter 就是发送键）
'''

if "全部用纯 Enter" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点，看当前代码")
    i = text.find("_mods")
    if i >= 0:
        print(repr(text[i-100:i+200]))
else:
    bak = TARGET.with_suffix(".py.bak_sendfinal")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ QUEST 已改回纯 Enter")