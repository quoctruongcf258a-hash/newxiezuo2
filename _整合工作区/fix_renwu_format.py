# fix_renwu_format.py — 人物设计环节的输出格式改成"多人多文件"
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    key = phase_cfg.get("key", "")
    if program == "规划":
        # 从 desc 拆出字段模板
'''

NEW = '''    key = phase_cfg.get("key", "")
    if program == "规划":
        # 人物设计：多人多文件
        if key == "人物设计":
            return (
                "本环节**为每个人物生成一份独立文件**（不是所有人挤在一个文件里）。\\n\\n"
                "第一步：先读项目信息.json 的 `人物设计列表` 字段，拿到人物名单。\\n\\n"
                "第二步：为列表中**每个名字**输出一份档案，格式如下（每份文件一个 .md）：\\n"
                "  # 人物设计：<人物名>\\n"
                "  基础信息：<性别/年龄/身份/出身>\\n"
                "  外貌：<身高/体型/标志性特征>\\n"
                "  性格：<3-5 个关键词 + 说明>\\n"
                "  表层欲望：<他想要什么>\\n"
                "  深层欲望：<他真正需要什么>\\n"
                "  恐惧：<最怕什么>\\n"
                "  创伤：<过去发生了什么>\\n"
                "  秘密：<他隐藏什么>\\n"
                "  能力：<能力/功法>\\n"
                "  能力代价：<使用代价>\\n"
                "  弱点：<软肋/破绽>\\n"
                "  口癖标志：<口头禅/动作特征>\\n"
                "  初始状态：<出场时的处境/境界>\\n"
                "  终局状态：<结局时的处境/境界>\\n"
                "  成长弧光：<从 ___ 到 ___>\\n"
                "  功法：<该人物使用的功法体系>\\n"
                "  宝物：<该人物持有的宝物>\\n"
                "  获取时间线：<何时获得功法/宝物/关键节点>\\n\\n"
                "**输出要求**：\\n"
                "  - 每个名字输出一段 `# 人物设计：<名字>` 开头的档案\\n"
                "  - 全部档案按人物列表顺序拼成一个 md 文件\\n"
                "  - 不要漏人、不要多人挤在一段"
            )
        # 从 desc 拆出字段模板
'''

text = TARGET.read_text(encoding="utf-8")

if "人物设计：<人物名>" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_renwu")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改：人物设计环节输出格式=多人多文件")