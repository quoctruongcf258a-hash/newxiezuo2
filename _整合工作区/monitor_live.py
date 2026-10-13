import sys, time
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy

print("=" * 70)
print("实时忙闲监控（Ctrl+C 停止）")
print("=" * 70)

AIS = ["WorkBuddy", "Doubao", "CodeBuddy", "gemini"]
round_n = 0
while True:
    round_n += 1
    line = ""
    for ai in AIS:
        try:
            busy = is_ai_busy(ai)
            line += f"{ai}={'🔴忙' if busy else '🟢闲'}  "
        except Exception as e:
            line += f"{ai}=⚠err  "
    print(f"[{time.strftime('%H:%M:%S')}] #{round_n:03d}  {line}")
    time.sleep(5)
