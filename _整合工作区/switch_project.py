# switch_project.py — 切换到独立测试项目
import json
import shutil
import datetime
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
OUTPUT = BASE / "output"
OLD_PROJ = "女王归来"
NEW_PROJ = "女王归来_test"

# 1) 复制 00_初始化 到新项目
src_init = OUTPUT / OLD_PROJ / "00_初始化"
dst_init = OUTPUT / NEW_PROJ / "00_初始化"
if dst_init.exists():
    print(f"⚠ {NEW_PROJ} 已存在，用新时间戳")
    NEW_PROJ = f"女王归来_test_{datetime.datetime.now().strftime('%H%M%S')}"
    dst_init = OUTPUT / NEW_PROJ / "00_初始化"

shutil.copytree(src_init, dst_init)
n = sum(1 for _ in dst_init.rglob('*') if _.is_file())
print(f"✔ 已复制 00_初始化（{n} 个文件）→ {dst_init}")

# 2) 更新 current_project.json
cfg = BASE / "windows-use" / "work" / "collab" / "current_project.json"
cfg.parent.mkdir(parents=True, exist_ok=True)
bak = cfg.with_suffix(".json.bak_switch") if cfg.exists() else None
if bak and not bak.exists():
    shutil.copy(cfg, bak)
    print(f"已备份：{bak.name}")

cfg.write_text(json.dumps({"project": NEW_PROJ}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✔ current_project.json → {NEW_PROJ}")

print()
print("=" * 60)
print(f"新测试项目: {NEW_PROJ}")
print(f"产物将落到: output\\{NEW_PROJ}\\")
print(f"原项目保留: output\\{OLD_PROJ}\\")
print("=" * 60)