# monitor_busy.py — 实时监控 4 个 AI 忙闲状态
import sys, time
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy

for _ in range(20):
    line = ""
    for ai in ["QUEST", "WorkBuddy", "Doubao", "gemini"]:
        try:
            busy = is_ai_busy(ai)
            line += f"{ai}={'忙' if busy else '闲'}  "
        except Exception as e:
            line += f"{ai}=err({e.__class__.__name__})  "
    print(f"[{time.strftime('%H:%M:%S')}] {line}")
    time.sleep(10)