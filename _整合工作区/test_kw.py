import json, sys
from pathlib import Path

# 把 orchestrator.py 所在目录加入 sys.path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

import orchestrator

# 加载 apps.json 和 rings_items.json
apps_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\apps.json")
rings_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")

apps = json.loads(apps_path.read_text(encoding="utf-8")) if apps_path.exists() else {}
rings = json.loads(rings_path.read_text(encoding="utf-8"))

targets = ["全书结构", "总纲规划", "粗纲规划", "简短细纲规划", "详细细纲规划"]

print("=== 新环 keywords_for_phase 实际返回结果 ===\n")
for ring in rings["01_规划"]["环节"]:
    name = ring.get("name", "")
    if name not in targets:
        continue
    fields = ring.get("fields") or []
    # 模拟 phase_cfg 结构
    phase_cfg = {
        "key": ring.get("code", ""),
        "name": name,
        "desc": ring.get("desc", ""),
        "fields": fields,
    }
    kw = orchestrator.keywords_for_phase(apps, "规划", phase_cfg)
    print(f"--- {ring.get('code')} {name} ---")
    print(f"  fields 有 {len(fields)} 项")
    print(f"  内容词 ({len(kw['内容词'])} 项): {kw['内容词']}")
    print(f"  动作词: {kw['动作词']}")
    print(f"  禁止词: {kw['禁止词']}")
    print(f"  验收词: {kw['验收词']}")
    print(f"  红线: {kw['红线']}")
    print()
