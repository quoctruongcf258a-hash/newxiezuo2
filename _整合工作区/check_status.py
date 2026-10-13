import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

print("=" * 60)
print("补丁状态检查")
print("=" * 60)

# 1. _resolve_ai_name 是否修好
for k in ["workbuddy", "doubao", "codebuddy", "gemini"]:
    try:
        real = orchestrator._resolve_ai_name(k)
        print(f"  _resolve_ai_name({k:12}) → {real}")
    except Exception as e:
        print(f"  _resolve_ai_name({k:12}) → ERR: {e}")

# 2. 停止机制是否装上
print()
print("  停止机制：")
for name in ["_STOP_FLAG", "_check_stop", "_install_hotkey_listener", "_request_stop"]:
    ok = hasattr(orchestrator, name)
    print(f"    {name}: {'[OK]' if ok else '[MISSING]'}")

# 3. keyboard 库
print()
try:
    import keyboard
    print("  keyboard 库：[OK]")
except ImportError:
    print("  keyboard 库：[MISSING] → 只能用 STOP.signal 文件")
