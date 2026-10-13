import sys
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

out_dir = r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test\01_规划\细纲"
stage = orchestrator._get_current_stage(out_dir)
print(f"=== _get_current_stage('{out_dir}') ===")
if stage:
    print(f"  [OK] 阶段号: {stage.get('阶段号')}")
    print(f"       起章: {stage.get('起章')}")
    print(f"       止章: {stage.get('止章')}")
    print(f"       季名: {stage.get('季名')}")
else:
    print(f"  [FAIL] 返回 None")
