# probe_audit.py — 看 apps.json 的 auditDirections 结构
import json
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\apps.json")
cfg = json.loads(P.read_text(encoding="utf-8"))

dirs = cfg.get("auditDirections") or []
print(f"auditDirections 共 {len(dirs)} 个方向\n")

for d in dirs:
    key = d.get("key") or d.get("name") or "?"
    rings = d.get("rings") or []
    extends = d.get("extends") or []
    std_count = len(d.get("standards") or [])
    fail_count = len(d.get("failPatterns") or [])
    print(f"【{key}】rings={rings}  extends={extends}")
    print(f"        standards={std_count} 条，failPatterns={fail_count} 条")