import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

import sys as _s
_wu = orchestrator.HERE.parent
if str(_wu) not in _s.path:
    _s.path.insert(0, str(_wu))
from mix_send import send, is_ai_busy, wait_idle
print(f"[OK] mix_send 三个函数都可导入")
print(f"     send={send}")
print(f"     is_ai_busy={is_ai_busy}")
print(f"     wait_idle={wait_idle}")
