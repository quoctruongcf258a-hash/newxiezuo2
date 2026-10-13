# extract_p16.py — 提取 P16 dry-run 的核心信息
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_check_p16b.txt")
t = p.read_bytes().decode("gb18030", errors="ignore")
lines = t.splitlines()

print(f"总行数: {len(lines)}")
print()

# 1) 参战 / 块数
for ln in lines:
    if "共" in ln and "块" in ln:
        print(f"[块数] {ln.strip()}")

print()

# 2) 卷名
卷seen = set()
for ln in lines:
    for i in range(1, 6):
        ch = "一二三四五"[i-1]
        if f"第{ch}卷" in ln:
            卷seen.add(f"第{ch}卷")
if 卷seen:
    print("[出现的卷名]")
    for v in sorted(卷seen):
        print(f"  {v}")
else:
    print("[没找到卷名]")

print()

# 3) 每块产出/盲审/拼接的概览
from collections import Counter
cnt = Counter()
for ln in lines:
    if "[产出 |" in ln or "产出 |" in ln:
        cnt["产出"] += 1
    elif "[盲审 |" in ln or "盲审 |" in ln:
        cnt["盲审"] += 1
    elif "[拼接 |" in ln or "拼接 |" in ln:
        cnt["拼接"] += 1
    elif "固定流程" in ln:
        cnt["固定流程(跳过)"] += 1

print("[任务统计]")
for k, v in cnt.items():
    print(f"  {k}: {v}")

print()
print("[最后 5 行]")
for ln in lines[-5:]:
    print(f"  {ln[:140]}")