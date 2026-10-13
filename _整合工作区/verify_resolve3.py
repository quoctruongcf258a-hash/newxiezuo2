import importlib
import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

import orchestrator
importlib.reload(orchestrator)

print("=" * 50)
print("重新加载后测试")
print("=" * 50)
for k in ["workbuddy", "doubao", "codebuddy", "gemini", "quest"]:
    real = orchestrator._resolve_ai_name(k)
    print(f"  {k:12} → {real}")

# 关键：CDP_APPS 判定
from mix_send import CDP_APPS
print()
print("=" * 50)
print("CDP_APPS 判定")
print("=" * 50)
for k in ["workbuddy", "doubao", "codebuddy", "gemini"]:
    real = orchestrator._resolve_ai_name(k)
    in_cdp = real in CDP_APPS
    print(f"  {k:12} → {real:12} in CDP_APPS = {in_cdp}")
