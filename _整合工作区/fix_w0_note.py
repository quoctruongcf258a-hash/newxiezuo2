# fix_w0_note.py — format_note 加 W0_细纲分析 分支
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    if program == "写作":
        if key == "章前对齐卡":
'''

NEW = '''    if program == "写作":
        # W0_细纲分析：把本章 16 项细纲展开为写作素材
        if key == "W0_细纲分析" or "细纲分析" in key:
            return (
                "把本章的详细细纲展开为写作可用的素材，按下面结构逐项输出（一行一项）：\\n"
                "  【本章一句话】：用一句话概括本章\\n"
                "  【目标】：主角本章想做什么\\n"
                "  【阻力】：什么在阻止他\\n"
                "  【代价】：失败要付出什么\\n"
                "  【时间锚点】：本章发生在故事时间轴的什么位置\\n"
                "  【章内跨度】：本章覆盖多长时间\\n"
                "  【与上章时差】：距离上一章多久\\n"
                "  【倒计时状态】：是否有倒计时在走\\n"
                "  【爽点】：读者的爽感来自哪里\\n"
                "  【叙事线归属】：属于哪条叙事线（主线/支线/暗线）\\n"
                "  【对手层级】：本章对手是什么级别\\n"
                "  【视角】：用谁的视角叙述\\n"
                "  【关键实体】：本章出现的关键人物、物品、地点\\n"
                "  【本章变化】：本章结束时世界/人物发生了什么不可逆的变化\\n"
                "  【章末未闭合问题】：留给下一章的悬念\\n"
                "  【六要素阶段】：本章处于六要素的哪个阶段\\n"
                "  【钩子类型】：章末使用哪种钩子"
            )
        if key == "章前对齐卡":
'''

text = TARGET.read_text(encoding="utf-8")

if "把本章的详细细纲展开为写作可用的素材" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点，把 289-295 行贴出来")
else:
    bak = TARGET.with_suffix(".py.bak_w0")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已加 W0_细纲分析 的 format_note 分支")