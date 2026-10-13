# probe_findinput.py — 看 _FIND_INPUT_JS / _SCORE_JS / CDP_APPS 配置
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "文件前 130 行（配置 + JS 常量）", "=" * 30)
for i in range(0, 130):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")