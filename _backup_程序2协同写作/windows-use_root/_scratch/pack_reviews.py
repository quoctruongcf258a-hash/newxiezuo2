import os, re, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 只做一件事：把 30 份评审原文按"被审者"打包
# 因为你说"不理想情况下摘好的组合"，让 QUEST 自己读原文判断更靠谱

OUTDIR = os.path.join(R, "QUEST", "融合", "评审汇总")
os.makedirs(OUTDIR, exist_ok=True)

for target in P:
    chunks = []
    for reviewer in P:
        if reviewer == target: continue
        fp = os.path.join(R, reviewer, "评审", "规划轮", f"评审_{target}.md")
        if not os.path.exists(fp): continue
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            t = f.read()
        chunks.append(f"\n\n{'='*70}\n## 来自 {reviewer} 的评审\n{'='*70}\n\n{t}")
    out = os.path.join(OUTDIR, f"对{target}的评审_5份.md")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(f"# 对 {target} 的规划 · 5 位评审汇总\n")
        f.write("".join(chunks))
    print(f"✅ {os.path.basename(out)}  ({os.path.getsize(out)/1024:.1f} KB)")

print("\n输出目录:", OUTDIR)