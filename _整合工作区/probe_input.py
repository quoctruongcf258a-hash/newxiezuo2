# probe_input.py — 看 CDPTab 怎么定位聊天输入框
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

def show(a, b, title):
    print("=" * 30, title, "=" * 30)
    for i in range(a-1, min(b, len(lines))):
        print(f"{i+1:4d}| {lines[i]}")

show(283, 330, "_is_slate_input")
show(331, 360, "send_text 开头")
show(361, 425, "_click_box")
show(126, 195, "CDPTab.__init__ / cmd / js")