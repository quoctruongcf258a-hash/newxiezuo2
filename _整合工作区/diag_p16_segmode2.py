import json
from pathlib import Path

# 1. rings_items.json 里 P16 的完整配置
rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
print("=== P16 完整配置（rings_items.json）===")
for ring in rings["01_规划"]["环节"]:
    if ring.get("code") == "P16":
        print(json.dumps(ring, ensure_ascii=False, indent=2))

# 2. 全盘搜索 segment_mode
print("\n=== 全盘搜索 segment_mode ===")
root = Path(r"F:\赛马23环整合工作室\程序2改装版\rules")
for f in root.rglob("*.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue

    def scan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "segment_mode":
                    print(f"  📄 {f.name}  {path}.{k} = {v!r}")
                scan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                scan(item, f"{path}[{i}]")
    scan(data)

# 3. _parse_volumes 函数
print("\n=== _parse_volumes 函数 ===")
target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines):
    if "def _parse_volumes" in ln:
        for j in range(i, min(i+35, len(lines))):
            print(f"  {j+1:4d}| {lines[j]}")
        break

# 4. chunks_for_phase 里的 segment_mode 分支完整代码
print("\n=== chunks_for_phase 里的 segment_mode 分支 ===")
for i, ln in enumerate(lines):
    if "def chunks_for_phase" in ln:
        for j in range(i, min(i+100, len(lines))):
            print(f"  {j+1:4d}| {lines[j]}")
        break
