import json, shutil
from pathlib import Path

f = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\today.json")
bak = f.with_suffix(".json.bak_no_cb")

if not bak.exists():
    print(f"❌ 找不到备份 {bak}")
    raise SystemExit()

# 恢复备份（含 codebuddy）
shutil.copy(bak, f)
data = json.loads(f.read_text(encoding="utf-8"))
print(f"✅ 已恢复")
print(f"   阵容：{[x['key'] for x in data['opened']]}")
print(f"   拼接者：{data.get('merge_app')}")
