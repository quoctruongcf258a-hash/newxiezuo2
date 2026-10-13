import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy
import time

print("完整 is_ai_busy 测试：")
for ai in ["Doubao", "CodeBuddy"]:
    t0 = time.time()
    try:
        r = is_ai_busy(ai)
        dt = time.time() - t0
        print(f"  {ai:12}  -> {r}  (耗时 {dt:.2f}s)")
    except Exception as e:
        print(f"  {ai:12}  -> 异常：{e}")
