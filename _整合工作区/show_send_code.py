# show_send_code.py — 看当前发送逻辑的实际代码
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

# 找 "# 5. 发送" 或 "_mods" 附近
for i, ln in enumerate(lines):
    if "发送" in ln and ("5." in ln or "补丁" in ln):
        print(f"--- 从第 {i+1} 行起 ---")
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1:4d}| {lines[j]}")
        break
else:
    # 没找到就找 _mods
    for i, ln in enumerate(lines):
        if "_mods" in ln:
            print(f"--- _mods 附近（第 {i+1} 行） ---")
            for j in range(max(0, i-20), min(i+40, len(lines))):
                print(f"{j+1:4d}| {lines[j]}")
            break