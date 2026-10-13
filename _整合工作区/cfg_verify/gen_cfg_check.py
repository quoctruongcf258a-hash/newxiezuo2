# -*- coding: utf-8 -*-
"""对比：全局手写模板 vs 项目 config 自动生成的模板，找出环节提示词的问题。"""
import io, os, sys, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)
import build_project_config as bpc
import paths

OUT = r"F:\赛马23环整合工作室\_整合工作区\cfg_verify\gencfg"
shutil.rmtree(OUT, ignore_errors=True)
res = bpc.build_config("通用37环", OUT)
print("生成:", res)

GLOBAL = paths.PROMPTS_DIR
print("\n全局 prompts 根:", GLOBAL)

for st in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
    gdir = os.path.join(GLOBAL, st)
    cdir = os.path.join(OUT, "prompts", st)
    g = sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []
    c = sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []
    print("\n[%s] 全局 %d 个 / 项目级 %d 个" % (st, len(g), len(c)))
    if g:
        print("   全局:", ", ".join(g[:8]), "..." if len(g) > 8 else "")

for rel in ("03_去AI/R1_润色.md", "02_写作/W1_章前对齐卡.md", "04_审核/Q1_逻辑设定一致.md"):
    p = os.path.join(OUT, "prompts", rel)
    print("\n" + "=" * 60)
    print("项目级:", rel)
    print("-" * 60)
    print(open(p, encoding="utf-8").read()[:700] if os.path.exists(p) else "  (不存在)")

p = os.path.join(OUT, "prompts", "02_写作", "W3_正文__始.md")
print("\n" + "=" * 60)
print("项目级: 02_写作/W3_正文__始.md")
print("-" * 60)
print(open(p, encoding="utf-8").read()[:600] if os.path.exists(p) else "  (不存在)")

g = os.path.join(GLOBAL, "02_写作", "W3_正文.md")
if os.path.exists(g):
    print("\n" + "=" * 60)
    print("全局: 02_写作/W3_正文.md（手写版）")
    print("-" * 60)
    print(open(g, encoding="utf-8").read()[:600])