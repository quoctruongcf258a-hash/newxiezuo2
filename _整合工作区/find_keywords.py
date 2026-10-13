from pathlib import Path

root = Path(r"F:\赛马23环整合工作室")

print("=== 搜索包含 keywords_for_phase 的文件 ===")
hits = []
for p in root.rglob("*.py"):
    # 跳过第三方库
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if "keywords_for_phase" in text:
        hits.append(p)
        print(f"  {p.relative_to(root)}")

print(f"\n共命中 {len(hits)} 个文件")

# 对每个命中文件，打印函数定义及其上下文
for h in hits[:5]:
    print(f"\n{'='*60}")
    print(f"📄 {h.relative_to(root)}")
    print(f"{'='*60}")
    text = h.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "keywords_for_phase" in line:
            # 打印上下 30 行
            start = max(0, i - 5)
            end = min(len(lines), i + 40)
            for j in range(start, end):
                marker = ">>> " if j == i else "    "
                print(f"{marker}{j+1:4d}| {lines[j]}")
            print("-" * 40)
