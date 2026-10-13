# fix_auditmap.py — 补丁3：把新环挂到正确的 auditDirections 方向下
import json
import shutil
from pathlib import Path

APPS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\apps.json")

ADD = {
    "定位与约束": ["文风与叙事基调"],
    "人物系统": ["人物设计"],
    "世界系统": ["门派与势力", "副本与任务线", "血脉与灵兽",
                 "地图与秘境", "宝物与传承", "天骄与对手"],
    "结构与结局": ["全书结构", "总纲规划", "粗纲规划",
                   "简短细纲规划", "详细细纲规划"],
}

data = json.loads(APPS.read_text(encoding="utf-8"))
dirs = data.get("auditDirections") or []

changed = 0
for d in dirs:
    key = d.get("key") or d.get("name") or ""
    if key not in ADD:
        continue
    extends = list(d.get("extends") or [])
    for name in ADD[key]:
        if name not in extends:
            extends.append(name)
            changed += 1
    d["extends"] = extends
    print(f"  {key}  →  {d['extends']}")

if changed:
    bak = APPS.with_suffix(".json.bak_auditmap")
    if not bak.exists():
        shutil.copy(APPS, bak)
        print(f"\n已备份：{bak.name}")
    APPS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✔ 共补 {changed} 个环名")
else:
    print("没有变化")