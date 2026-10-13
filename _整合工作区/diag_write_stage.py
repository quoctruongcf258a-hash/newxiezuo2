import json
from pathlib import Path

# ── 1. 02_写作 各环节完整配置 ──
rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
print("=== 02_写作 各环节配置 ===")
for ring in rings["02_写作"]["环节"]:
    print(f"\n--- {ring.get('code')} {ring.get('name')} ---")
    print(json.dumps(ring, ensure_ascii=False, indent=2))

# ── 2. 环节模板.json 里的写作环 ──
p2 = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\环节模板.json")
if p2.exists():
    d2 = json.loads(p2.read_text(encoding="utf-8"))
    print("\n=== 环节模板.json 含写作/章 的环 ===")
    for pool in ("固定环", "外围池"):
        for ring in d2.get(pool, []):
            name = ring.get("name", "")
            if any(k in name for k in ["W0", "W1", "W2", "W3", "W4", "细纲分析", "对齐卡", "分布", "正文", "节奏自检"]):
                print(f"\n--- {pool}: {name} ---")
                print(json.dumps(ring, ensure_ascii=False, indent=2))

# ── 3. P18 产出目录 ──
out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p18_dir = out_root / "01_规划" / "前30章落地章纲"
print(f"\n=== P18 产出目录 ===")
print(f"  存在: {p18_dir.exists()}")
if p18_dir.exists():
    for sub in p18_dir.iterdir():
        if sub.is_dir():
            print(f"    📁 {sub.name}/")
            files = list(sub.glob("*"))
            print(f"       共 {len(files)} 个文件")
            for f in sorted(files)[:3]:
                print(f"         {f.name}")
            if len(files) > 3:
                print(f"         ... (还有 {len(files)-3} 个)")

# ── 4. 现有 SPLIT_SOURCES 配置 ──
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
print("\n=== SPLIT_SOURCES 现状 ===")
for k, v in orchestrator.SPLIT_SOURCES.items():
    print(f"  {k}: {v}")
