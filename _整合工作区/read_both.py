import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("[1] _build_batch_prompt 完整代码")
print("=" * 70)
print(inspect.getsource(orchestrator._build_batch_prompt))

print()
print("=" * 70)
print("[2] phase_input 里含「本环节输出路径」的代码")
print("=" * 70)
src = inspect.getsource(orchestrator.phase_input)
i = src.find("本环节输出路径")
if i >= 0:
    print(src[max(0,i-200):i+400])
