# patch_upstream.py — _upstream_files 加读「用户输入.md」
from pathlib import Path

O = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = O.read_text(encoding="utf-8")

OLD = '''        # 00_初始化 现在只读：梗概 + 卷纲（其余交给 AI 环节自由拓展）
        for _bp in ("第0步梗概.md", "1.6_卷纲.md"):'''

NEW = '''        # 00_初始化 读取：用户输入 + 梗概 + 卷纲
        for _bp in ("用户输入.md", "第0步梗概.md", "1.6_卷纲.md"):'''

if "用户输入.md" in text and "读取：用户输入" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("只读：梗概")
    if i >= 0:
        print(repr(text[i-100:i+300]))
else:
    text = text.replace(OLD, NEW, 1)
    O.write_text(text, encoding="utf-8")
    print("OK 已加读 用户输入.md")