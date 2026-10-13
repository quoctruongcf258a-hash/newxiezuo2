import json
from pathlib import Path

# ── 1. 03_去AI 全部环节 ──
rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
print("=== 03_去AI 各环节配置 ===")
for ring in rings.get("03_去AI", {}).get("环节", []):
    print(json.dumps(ring, ensure_ascii=False, indent=2))

# ── 2. 04_审核 全部环节 ──
print("\n\n=== 04_审核 各环节 ===")
for ring in rings.get("04_审核", {}).get("环节", []):
    print(f"  {ring.get('code')}  {ring.get('name')}  type={ring.get('type')}  fields={ring.get('fields')}")

# ── 3. 05_出厂 全部环节 ──
print("\n\n=== 05_出厂 各环节 ===")
for ring in rings.get("05_出厂", {}).get("环节", []):
    print(f"  {ring.get('code')}  {ring.get('name')}  type={ring.get('type')}")

# ── 4. 现有 SPLIT_SOURCES / SPLIT_PRODUCERS ──
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
print("\n\n=== SPLIT_SOURCES 现状 ===")
for k, v in orchestrator.SPLIT_SOURCES.items():
    print(f"  {k}: {v}")
print("\n=== SPLIT_PRODUCERS 现状 ===")
for k, v in orchestrator.SPLIT_PRODUCERS.items():
    print(f"  {k}: {v}")

# ── 5. phase_input 里对"润色"的处理 ──
target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()
print("\n\n=== phase_input 里 program == 润色 / 质检 分支 ===")
for i, ln in enumerate(lines):
    if 'program == "润色"' in ln or 'program == "质检"' in ln:
        for j in range(max(0, i-2), min(i+12, len(lines))):
            print(f"  {j+1:4d}| {lines[j]}")
        print("  " + "-"*40)
