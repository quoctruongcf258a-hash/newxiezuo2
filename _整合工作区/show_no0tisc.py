# show_no0tisc.py — 看 no0tisc.md 全文
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\prompts\步骤0\no0tisc.md")
print(f"文件: {p}")
print(f"字节: {p.stat().st_size}")
print("=" * 75)
print(p.read_text(encoding="utf-8"))