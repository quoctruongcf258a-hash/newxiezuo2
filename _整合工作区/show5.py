import os
from pathlib import Path

base_dir = Path(".")
print("正在查找 _v1.txt 到 _v5.txt ...\n")

for i in range(1, 6):
    file = base_dir / f"_v{i}.txt"
    if file.exists():
        content = file.read_text(encoding="utf-8")
        print(f"====== _v{i}.txt (总长 {len(content)} 字符) ======")
        print(content[:1500]) # 先看前1500字，防止刷屏
        if len(content) > 1500:
            print("\n... (内容过长，已截断)")
        print("\n" + "="*50 + "\n")
    else:
        print(f"⚠️ 未找到: {file.absolute()}")
