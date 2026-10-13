# P09 不需要预改 split.json（它是源头）
# 但需要确认 00_初始化 齐全
from pathlib import Path
import json

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
init_dir = proj_root / "00_初始化"

print("=== 00_初始化 内容 ===")
for f in init_dir.iterdir():
    print(f"  {f.name}  ({f.stat().st_size}B)")

print("\n=== 项目信息 ===")
info = json.loads((init_dir / "项目信息.json").read_text(encoding="utf-8"))
print(json.dumps(info, ensure_ascii=False, indent=2))
