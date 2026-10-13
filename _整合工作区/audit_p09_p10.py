import json
from pathlib import Path

# ── 1. 项目信息.json 完整字段 ──
info_path = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来\00_初始化\项目信息.json")
info = json.loads(info_path.read_text(encoding="utf-8"))
print("=== 项目信息.json 所有字段 ===")
for k, v in info.items():
    if isinstance(v, list):
        print(f"  {k}: [列表 {len(v)}] {v[:3]}{'...' if len(v) > 3 else ''}")
    else:
        print(f"  {k}: {repr(v)[:100]}")

# ── 2. 查找 P09/P10/P15 已产出的文件 ──
print("\n\n=== P09/P10/P15 目录内容 ===")
out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来\01_规划")
for ring in ["全书结构", "分卷结构", "粗纲规划"]:
    d = out_root / ring
    print(f"\n📁 {ring}/  (存在: {d.exists()})")
    if d.exists():
        for f in sorted(d.rglob("*")):
            if f.is_file():
                rel = f.relative_to(d)
                print(f"    {rel}  ({f.stat().st_size}B)")

# ── 3. 打印 P09 的 merged 稿前 1500 字 ──
print("\n\n=== P09 全书结构 merged 稿（前 1500 字）===")
p09 = out_root / "全书结构" / "merged"
if p09.exists():
    for f in sorted(p09.glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        print(f"--- {f.name} (共 {len(text)} 字) ---")
        print(text[:1500])
        break
else:
    print(f"  {p09} 不存在")
    # 尝试从 phase_candidate.md 读
    pc = out_root / "全书结构" / "phase_candidate.md"
    if pc.exists():
        text = pc.read_text(encoding="utf-8", errors="ignore")
        print(f"--- phase_candidate.md (共 {len(text)} 字) ---")
        print(text[:1500])

# ── 4. 打印 P10 的 merged 稿前 1500 字 ──
print("\n\n=== P10 分卷结构 merged 稿（前 1500 字）===")
p10 = out_root / "分卷结构" / "merged"
if p10.exists():
    for f in sorted(p10.glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        print(f"--- {f.name} (共 {len(text)} 字) ---")
        print(text[:1500])
        break
else:
    print(f"  {p10} 不存在")
