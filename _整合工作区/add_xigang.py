# add_xigang.py — 在 phases.json 的 02_写作 开头加 W0 细纲分析
import json
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\phases.json")

data = json.loads(TARGET.read_text(encoding="utf-8"))
写作 = data.get("环节", {}).get("02_写作", [])

exists = any((isinstance(x, dict) and x.get("name", "").startswith("W0"))
             or (isinstance(x, str) and x.startswith("W0"))
             for x in 写作)

if exists:
    print("已存在 W0，跳过")
else:
    bak = TARGET.with_suffix(".json.bak_xigang")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    W0 = {
        "name": "W0_细纲分析",
        "mode": "mesh",
        "desc": "把本章的详细细纲（16 项）拆解为写作可用的素材",
        "fields16": [
            "目标", "阻力", "代价", "时间锚点", "章内跨度",
            "与上章时差", "倒计时状态", "爽点", "叙事线归属", "对手层级",
            "视角", "关键实体", "本章变化", "章末未闭合问题",
            "六要素阶段", "钩子类型"
        ]
    }
    写作.insert(0, W0)
    data["环节"]["02_写作"] = 写作
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("✔ 已在 02_写作 开头插入 W0_细纲分析")
    print(f"  现在 02_写作 有 {len(写作)} 环")
    for i, x in enumerate(写作, 1):
        if isinstance(x, dict):
            print(f"    {i}. {x.get('name')}")
        else:
            print(f"    {i}. {x}")