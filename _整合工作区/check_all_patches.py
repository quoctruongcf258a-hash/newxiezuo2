import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

print("=" * 60)
print("停止机制检查")
print("=" * 60)
for name in ["_STOP_FLAG", "_check_stop", "_request_stop", "_sleep_breakable", "_install_hotkey_listener"]:
    print(f"  {name}: {'[OK]' if hasattr(orchestrator, name) else '[MISSING]'}")

# 检查 tasks.py 的 FILE_MODE_AIS
import tasks
print()
print(f"  FILE_MODE_AIS: {tasks.FILE_MODE_AIS}")
print(f"  codebuddy 在内: {'✅' if 'codebuddy' in tasks.FILE_MODE_AIS else '❌ 需要修'}")

# 检查 keyboard 装在哪个 Python
try:
    import keyboard
    print(f"  keyboard 在 orchestrator 环境: ✅")
except ImportError:
    print(f"  keyboard 在 orchestrator 环境: ❌")
