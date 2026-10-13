from pathlib import Path

base_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
targets = ["P09", "P14", "P15", "P16", "P17",
           "全书结构", "总纲规划", "粗纲规划", "简短细纲", "详细细纲",
           "三幕", "主线弧光", "故事内容摘要", "故事底色",
           "章序号", "每章一句话", "31-60章"]

for i in range(1, 6):
    file = base_dir / f"_v{i}.txt"
    if not file.exists():
        print(f"⚠️ 未找到: {file}")
        continue

    content = file.read_text(encoding="utf-8")
    lines = content.splitlines()

    print(f"\n{'='*60}")
    print(f"📄 _v{i}.txt  (共 {len(lines)} 行, {len(content)} 字符)")
    print(f"{'='*60}")

    # 搜索目标关键词所在的行
    hits = []
    for idx, line in enumerate(lines):
        for t in targets:
            if t in line:
                hits.append((idx, t, line[:120]))
                break

    if not hits:
        print("  ❌ 没找到任何目标关键词（P09/P14/P15/P16/P17/三幕/章序号等）")
        print("  文件末尾 20 行:")
        for line in lines[-20:]:
            print(f"    | {line[:100]}")
        continue

    print(f"  命中 {len(hits)} 处，显示前 30 处：\n")
    seen = set()
    for idx, t, snippet in hits[:30]:
        key = (idx, t)
        if key in seen:
            continue
        seen.add(key)
        print(f"  [第{idx}行] 命中「{t}」")
        print(f"    {snippet}")
        print()
