import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import json

# 读 P09 的配置
rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
for ring in rings["01_规划"]["环节"]:
    if ring.get("name") == "全书结构":
        phase_cfg = dict(ring)
        note = orchestrator.format_note("规划", phase_cfg)
        print("=== P09 的 format_note 输出 ===")
        print(note)
        break
