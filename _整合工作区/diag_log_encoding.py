from pathlib import Path

log = Path(r"F:\赛马23环整合工作室\_整合工作区\p09_log.txt")
raw = log.read_bytes()
print(f"文件大小：{len(raw)}B")
print(f"前 3 字节：{raw[:3]!r}")
print()

# 尝试多种编码读
for enc in ["utf-8", "gbk", "utf-8-sig"]:
    try:
        text = raw.decode(enc, errors="replace")
        print(f"=== {enc} 前 500 字 ===")
        print(text[:500])
        print()
    except Exception as e:
        print(f"{enc}: 失败 {e}")
        print()
