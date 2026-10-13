import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)

# 模拟 P09 的 phase_cfg
phase_cfg = {
    "code": "P09",
    "name": "全书结构",
    "desc": "三幕/五幕划分 + 主线弧光 + 全书大结构锚点",
    "expert_role": "小说结构规划师",
}

# 模拟 cfg
cfg = {}

# 调用 phase_input（会输出很长，只取前 300 字）
out = orchestrator.phase_input(cfg, "规划", phase_cfg, None)
print("=" * 60)
print("phase_input 输出前 300 字：")
print("=" * 60)
print(out[:300])
