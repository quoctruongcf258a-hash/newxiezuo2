# -*- coding: utf-8 -*-
"""盘点已有项目的 config/prompts 健康度（是否含旧的坏模板）。"""
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOTS = [
    r"F:\赛马23环整合工作室\程序2改装版\output",
    r"F:\赛马23环整合工作室\程序2改装版\workspace",
]
BAD_PLACEHOLDER = re.compile(r"(?<!\{)\{(输入|平台规则|产物目录)\}")
HOLLOW = "见上游资料与全局规划"

projects = []
for root in ROOTS:
    if not os.path.isdir(root):
        continue
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if os.path.isdir(p):
            projects.append(p)

print("扫描根目录:", ROOTS)
print("发现项目 %d 个\n" % len(projects))
need_fix = []
for p in projects:
    cfg = os.path.join(p, "config")
    if not os.path.isdir(cfg):
        continue
    pd = os.path.join(cfg, "prompts")
    if not os.path.isdir(pd):
        print("[%s]  无 config/prompts（引擎将回退全局模板）" % os.path.basename(p))
        continue
    bad, hollow, total = [], [], 0
    for st in os.listdir(pd):
        sd = os.path.join(pd, st)
        if not os.path.isdir(sd):
            continue
        for f in os.listdir(sd):
            if not f.endswith(".md"):
                continue
            total += 1
            txt = open(os.path.join(sd, f), encoding="utf-8", errors="replace").read()
            if BAD_PLACEHOLDER.search(txt):
                bad.append("%s/%s" % (st, f))
            elif HOLLOW in txt:
                hollow.append("%s/%s" % (st, f))
    tag = "✅ 健康" if not bad and not hollow else "⚠ 需重建"
    print("[%s]  %s  模板 %d 个｜坏占位符 %d｜空洞 %d" %
          (os.path.basename(p), tag, total, len(bad), len(hollow)))
    if bad or hollow:
        need_fix.append(p)
        if bad:
            print("     坏占位符示例:", ", ".join(bad[:4]))
        if hollow:
            print("     空洞示例:", ", ".join(hollow[:4]))

print("\n需要修复的项目：", need_fix if need_fix else "无")