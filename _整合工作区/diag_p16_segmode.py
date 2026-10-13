import json
from pathlib import Path

# 1. rings_items.json 里 P16 的 segment_mode
rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
print("=== rings_items.json 里 01_规划 有 segment_mode 的环节 ===")
for ring in rings["01_规划"]["环节"]:
    sm = ring.get("segment_mode")
    if sm:
        print(f"  {ring.get('code')} {ring.get('name')}: segment_mode = {sm!r}")

# 2. phases.json 里是否有
pj = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\phases.json")
if pj.exists():
    data = json.loads(pj.read_text(encoding="utf-8"))
    print(f"\n=== phases.json 顶层键：{list(data.keys())} ===")
    def scan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "segment_mode":
                    print(f"  {path}.{k} = {v!r}")
                scan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                scan(item, f"{path}[{i}]")
    scan(data)

# 3. 也看 apps.json
aj = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\apps.json")
if aj.exists():
    data2 = json.loads(aj.read_text(encoding="utf-8"))
    print(f"\n=== apps.json 顶层键：{list(data2.keys())} ===")
    def scan2(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "segment_mode":
                    print(f"  {path}.{k} = {v!r}")
                scan2(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                scan2(item, f"{path}[{i}]")
    scan2(data2)

# 4. _parse_volumes 函数
print("\n=== _parse_volumes 函数 ===")
target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines):
    if "def _parse_volumes" in ln:
        for j in range(i, min(i+30, len(lines))):
            print(f"  {j+1:4d}| {lines[j]}")
        break
