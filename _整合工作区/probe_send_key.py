# probe_send_key.py — 看 send_text 结尾发送逻辑 + QUEST 特殊处理
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "send_text 尾部（415-460 行）", "=" * 30)
for i in range(414, 460):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")

print()
print("=" * 30, "全文含 ctrl/control/Ctrl/ENTER/Enter/发送 的行", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["ctrl", "Ctrl", "control", "Control",
                              "ENTER", "ctrlenter", "quest", "QUEST", "Quest",
                              "发送", "send_btn", "click_send"]):
        print(f"{i:4d}| {ln[:140]}")

print()
print("=" * 30, "cdp_qw_ctrlenter.py 内容", "=" * 30)
Q = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\cdp_qw_ctrlenter.py")
if Q.exists():
    print(Q.read_text(encoding="utf-8", errors="ignore"))
else:
    print("不存在")