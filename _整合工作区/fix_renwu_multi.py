# fix_renwu_multi.py — 人物设计改成"AI 依次保存 N 个文件"
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''        if key == "人物设计":
            return (
                "本环节**为每个人物生成一份独立文件**（不是所有人挤在一个文件里）。\\n\\n"
                "第一步：先读项目信息.json 的 `人物设计列表` 字段，拿到人物名单。\\n\\n"
                "第二步：为列表中**每个名字**输出一份档案，格式如下（每份文件一个 .md）：\\n"
'''

NEW = '''        if key == "人物设计":
            return (
                "本环节**为每个人物生成一份独立文件**。\\n\\n"
                "第一步：先读项目信息.json 的 `人物设计列表` 字段，拿到人物名单（N 个人）。\\n\\n"
                "第二步：为列表中**每个名字**输出一份档案，格式如下（每份一份 .md）：\\n"
'''

text = TARGET.read_text(encoding="utf-8")

if "为每个人物生成一份独立文件" in text and "N 个人" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点，先看当前代码")
    # 打印当前位置
    i = text.find("人物设计：<人物名>")
    if i >= 0:
        print(text[i-200:i+200])
else:
    bak = TARGET.with_suffix(".py.bak_renwumulti")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改：提示词告知 AI 有 N 个人")