import sys
import time
from pathlib import Path
from datetime import datetime

WU = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use")
sys.path.insert(0, str(WU))

from mix_send import is_ai_busy

# 从 today.json 读当前阵容
import json
TODAY = WU / "_scratch" / "today.json"
data = json.loads(TODAY.read_text(encoding="utf-8"))
ais = [(item["key"], item.get("label") or item["key"]) for item in data.get("opened", [])]

print("=" * 70)
print("AI 忙闲监控 · 每 3 秒一轮 · Ctrl+C 退出")
print("=" * 70)
print("监控对象：")
for k, lb in ais:
    print(f"  · {k} ({lb})")
print("=" * 70)
print("空闲时全部应显示 -（False）")
print("给某个 AI 发一句话，它应该变 + （True），答完再变回 -")
print("=" * 70)
print()

while True:
    line_parts = []
    for key, label in ais:
        try:
            busy = is_ai_busy(label)
            mark = "+" if busy else "-"
            line_parts.append(f"{label}:{mark}")
        except Exception as e:
            line_parts.append(f"{label}:ERR")
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}]  " + "   ".join(line_parts))
    time.sleep(3)