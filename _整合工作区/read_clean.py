# read_clean.py — 读混合编码日志（UTF-8 优先，fallback GBK）
import sys
from pathlib import Path

p = Path(sys.argv[1])
raw = p.read_bytes()

# 策略 1：UTF-8 严格
try:
    t = raw.decode("utf-8")
    cn = sum(1 for c in t if '\u4e00' <= c <= '\u9fff')
    print(f"[UTF-8] 中文字符 {cn} 个")
except Exception:
    # 策略 2：GBK
    t = raw.decode("gb18030", errors="replace")
    print(f"[GB18030] 已解码")

# 输出
for i, ln in enumerate(t.splitlines()):
    print(f"{i+1:4d}| {ln[:150]}")