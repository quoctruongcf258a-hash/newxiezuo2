# probe_send.py — 看 send_via_cdp + send 完整代码
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

def show(start, end, title):
    print("=" * 30, title, "=" * 30)
    for i in range(start-1, min(end, len(lines))):
        print(f"{i+1:4d}| {lines[i]}")

show(560, 610, "send_via_cdp 附近")
show(705, 748, "send 函数")