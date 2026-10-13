import json
from pathlib import Path

out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
pj = out_root / "进度.json"
if not pj.exists():
    print(f"找不到 {pj}")
    raise SystemExit(1)

data = json.loads(pj.read_text(encoding="utf-8"))
cur = data.get("当前阶段", 1)
total = data.get("总阶段数", 1)
if cur >= total:
    print(f"已经是最后一个阶段（{cur}/{total}）")
    raise SystemExit(0)

data["已完成阶段"] = list(set(data.get("已完成阶段", []) + [cur]))
data["当前阶段"] = cur + 1
pj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已推进：阶段 {cur} → {cur+1}（共 {total}）")
