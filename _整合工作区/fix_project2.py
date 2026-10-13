# fix_project2.py — 删除多余测试目录 + 改正确的 current_project.json
import json
import shutil
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
OUTPUT = BASE / "output"

# 1) 删多余的 test 目录
extra = OUTPUT / "女王归来_test_205830"
if extra.exists():
    shutil.rmtree(extra)
    print(f"✔ 删除 {extra.name}")

# 2) 改正确的 current_project.json
PROJECT_FILE = BASE / "work" / "collab" / "current_project.json"
PROJECT_FILE.parent.mkdir(parents=True, exist_ok=True)
if PROJECT_FILE.exists():
    bak = PROJECT_FILE.with_suffix(".json.bak_fix2")
    if not bak.exists():
        shutil.copy(PROJECT_FILE, bak)
        print(f"已备份：{bak.name}")
    print(f"原内容：{PROJECT_FILE.read_text(encoding='utf-8')}")
PROJECT_FILE.write_text(json.dumps({"project": "女王归来_test"}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✔ {PROJECT_FILE}")
print(f"   新内容：{PROJECT_FILE.read_text(encoding='utf-8')}")

# 3) 验证
import sys
sys.path.insert(0, str(BASE / "windows-use" / "_scratch"))
# 清掉可能已缓存的 orchestrator
for m in list(sys.modules.keys()):
    if 'orchestrator' in m:
        del sys.modules[m]
import orchestrator as O
print()
print(f"✔ _project_root() = {O._project_root()}")