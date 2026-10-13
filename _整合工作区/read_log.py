# read_log.py — 兼容多种编码读日志
import sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1
         else r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_real.txt")

raw = p.read_bytes()
print(f"文件大小: {len(raw)} 字节")
print(f"前 4 字节: {raw[:4].hex()}")
print()

# 尝试多种解码
best = None
best_score = -1
for enc in ["utf-8", "utf-8-sig", "gbk", "gb18030", "utf-16-le", "utf-16-be"]:
    try:
        t = raw.decode(enc, errors="ignore")
        # 中文占比作为评分
        cn = sum(1 for c in t if '\u4e00' <= c <= '\u9fff')
        good = sum(1 for w in ["失败", "重试", "CDP", "接口", "结束", "错误"] if w in t)
        score = cn + good * 100
        print(f"{enc:12s}  中文字符 {cn:6d}  关键词 {good}")
        if score > best_score:
            best_score = score
            best = (enc, t)
    except Exception as e:
        print(f"{enc:12s}  {e}")

if best:
    enc, t = best
    print(f"\n最佳编码: {enc}")
    print("=" * 70)
    # 打印最后 40 行
    for ln in t.splitlines()[-40:]:
        print(ln[:160])