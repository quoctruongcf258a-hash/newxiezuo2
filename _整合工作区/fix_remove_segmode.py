import json, shutil
from pathlib import Path

# ── 1. rings_items.json ──
p1 = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
bak1 = p1.with_suffix(".json.bak_segmode")
if not bak1.exists():
    shutil.copy(p1, bak1)
    print(f"已备份：{bak1.name}")

data = json.loads(p1.read_text(encoding="utf-8"))
removed = []
for ring in data["01_规划"]["环节"]:
    if ring.get("code") in ("P16", "P17") and "segment_mode" in ring:
        sm = ring.pop("segment_mode")
        removed.append(f"{ring['code']} {ring['name']}: segment_mode={sm!r}")
        # 顺便清掉 segment_size（如果有）
        if "segment_size" in ring:
            ring.pop("segment_size")
            removed[-1] += "（同时清 segment_size）"

for r in removed:
    print(f"  [DEL] {r}")

p1.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n已写回：{p1.name}")

# ── 2. 环节模板.json ──
p2 = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\环节模板.json")
if p2.exists():
    bak2 = p2.with_suffix(".json.bak_segmode")
    if not bak2.exists():
        shutil.copy(p2, bak2)
        print(f"已备份：{bak2.name}")

    d2 = json.loads(p2.read_text(encoding="utf-8"))
    fixed = 0
    for ring in d2.get("固定环", []):
        if "segment_mode" in ring:
            print(f"  [DEL] 环节模板: {ring.get('name')} segment_mode={ring.pop('segment_mode')!r}")
            fixed += 1
            if "segment_size" in ring:
                ring.pop("segment_size")
    if fixed:
        p2.write_text(json.dumps(d2, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已写回：{p2.name}（{fixed} 处）")

# ── 3. 验证 ──
print("\n=== 验证：还剩哪些 segment_mode ===")
for f in (p1, p2):
    if not f.exists():
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    def scan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "segment_mode":
                    print(f"  {f.name}  {path}.{k} = {v!r}")
                scan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                scan(item, f"{path}[{i}]")
    scan(d)
