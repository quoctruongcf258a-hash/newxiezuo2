import json
from pathlib import Path

out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p15_dir = out_root / "01_规划" / "粗纲规划"
p15_dir.mkdir(parents=True, exist_ok=True)

items = [{"key": f"章{ch}", "name": f"第{ch}章", "start": ch, "end": ch, "note": f"第{ch}章要点"}
         for ch in range(1, 151)]

data = {"拆分维度": "章", "环节": "P15", "环节名": "粗纲规划", "列表": items}
pj = p15_dir / "split.json"
pj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写：{pj}（{len(items)} 章）")
