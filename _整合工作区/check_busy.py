# check_busy.py — 只读 AI 忙闲
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy

for ai in ["QUEST", "WorkBuddy", "Doubao", "gemini"]:
    try:
        state = "忙" if is_ai_busy(ai) else "闲"
    except Exception as e:
        state = f"err({e.__class__.__name__})"
    print(f"  {ai}: {state}")