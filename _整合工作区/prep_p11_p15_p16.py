import json
from pathlib import Path

# ── 1. 看 P11/P15/P16 的配置 ──
rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
targets = ["P11", "P15", "P16"]
print("=== P11/P15/P16 配置 ===")
for ring in rings["01_规划"]["环节"]:
    if ring.get("code") in targets:
        print(f"\n--- {ring.get('code')} {ring.get('name')} ---")
        print(f"  desc: {ring.get('desc', '')[:150]}")
        print(f"  fields: {ring.get('fields')}")

# ── 2. 检查已有 fake split.json ──
out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
print("\n\n=== 已有 split.json 情况 ===")
for name in ["全书结构", "分卷结构", "粗纲规划"]:
    p = out_root / "01_规划" / name / "split.json"
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            items = d.get("列表") or []
            print(f"  [OK] {name}: {len(items)} 项")
            for it in items[:3]:
                print(f"      {it}")
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
    else:
        print(f"  [--] {name}: 不存在")

# ── 3. 造 fake P10 split.json（5 季）──
p10 = out_root / "01_规划" / "分卷结构" / "split.json"
if not p10.exists():
    seasons = []
    for i in range(1, 6):
        s = (i - 1) * 30 + 1
        e = i * 30
        seasons.append({
            "key": f"季{i}",
            "name": f"第{i}季",
            "start": s,
            "end": e,
            "note": f"第{i}季剧情",
        })
    p10.parent.mkdir(parents=True, exist_ok=True)
    data = {"拆分维度": "季", "环节": "P10", "环节名": "分卷结构", "列表": seasons}
    p10.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] 已造 fake P10 split.json：{len(seasons)} 季")
    for s in seasons:
        print(f"    {s['key']}  {s['start']}-{s['end']}  {s['note']}")
else:
    print(f"\n[SKIP] P10 split.json 已存在")
