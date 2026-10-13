import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 1. 扫章纲大小
print("=== 章纲大小 ===")
for p in P:
    d = os.path.join(R, p, "产出", "章纲轮")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        if "总稿" in fn: continue
        sz = os.path.getsize(os.path.join(d, fn))
        print(f"  {p:12} {fn:30} {sz:>7} B")

# 2. 打包评审汇总
OUT = os.path.join(R, "_融合产物", "章纲轮_评审汇总")
os.makedirs(OUT, exist_ok=True)
for target in P:
    chunks = []
    for reviewer in P:
        if reviewer == target: continue
        fp = os.path.join(R, reviewer, "评审", "章纲轮", f"评审_{target}.md")
        if not os.path.exists(fp): continue
        t = open(fp, encoding="utf-8", errors="ignore").read()
        chunks.append(f"\n\n{'='*70}\n## 来自 {reviewer} 的评审\n{'='*70}\n\n{t}")
    out = os.path.join(OUT, f"对{target}的评审_5份.md")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(f"# 对 {target} 章纲 · 5 位评审汇总\n" + "".join(chunks))
    print(f"✅ 对{target}的评审_5份.md  ({os.path.getsize(out)/1024:.1f} KB)")
