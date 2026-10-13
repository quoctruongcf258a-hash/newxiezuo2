import json
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
data = json.loads(p.read_text(encoding="utf-8"))

# 看 01_规划 前 3 环的完整字段
print("=" * 70)
print("01_规划 前 3 环完整字段")
print("=" * 70)
for ring in data["01_规划"]["环节"][:3]:
    print(json.dumps(ring, ensure_ascii=False, indent=2))
    print()

# 看 phase_input 注入 desc 的位置
print("=" * 70)
print("phase_input 注入 desc 的代码")
print("=" * 70)
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect
src = inspect.getsource(orchestrator.phase_input)
i = src.find("本环节任务说明")
if i >= 0:
    print(src[max(0,i-200):i+400])
