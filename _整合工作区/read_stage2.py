import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

src = inspect.getsource(orchestrator._run_batch_mesh)

# 打印【阶段2：盲审】整段
i = src.find("阶段2")
j = src.find("阶段3", i)
if j < 0:
    j = i + 2000
print("=" * 70)
print("_run_batch_mesh 阶段2（盲审）完整代码")
print("=" * 70)
print(src[i:j])
