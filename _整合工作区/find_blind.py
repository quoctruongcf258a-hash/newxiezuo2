# find_blind.py — 找盲审相关日志
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_final_run2.txt")
raw = p.read_bytes()

# 尝试多种编码
for enc in ["utf-8", "gb18030", "gbk"]:
    try:
        t = raw.decode(enc, errors="strict")
        print(f"=== {enc} 解码成功 ===")
        break
    except:
        continue
else:
    t = raw.decode("gb18030", errors="ignore")
    print("=== gb18030 ignore ===")

lines = t.splitlines()
print(f"总行数: {len(lines)}")
print()

# 找盲审关键行
keys = ["盲审", "并发", "review", "已抓取", "未抓到", "capture",
        "审 ", "审完", "无产出", "异常", "编排结束", "Traceback"]
for i, ln in enumerate(lines):
    if any(k in ln for k in keys):
        print(f"{i+1:4d}| {ln[:170]}")