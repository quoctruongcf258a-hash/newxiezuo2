import json
from pathlib import Path

out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p10_split = out_root / "01_规划" / "分卷结构" / "split.json"

if not p10_split.exists():
    print(f"找不到 {p10_split}")
    raise SystemExit(1)

data = json.loads(p10_split.read_text(encoding="utf-8"))
seasons = data.get("列表") or []

stages = []
for i, s in enumerate(seasons, start=1):
    stages.append({
        "阶段号": i,
        "起章": s.get("start") or 1,
        "止章": s.get("end") or 99999,
        "季名": s.get("name") or f"季{i}",
    })

progress = {"当前阶段": 1, "总阶段数": len(stages), "阶段列表": stages, "已完成阶段": []}
pj = out_root / "进度.json"
pj.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写：{pj}")
for s in stages:
    print(f"  阶段{s['阶段号']}  {s['起章']}-{s['止章']}  ({s['季名']})")
