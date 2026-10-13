# -*- coding: utf-8 -*-
import os, sys, json, tempfile, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
APP = r"F:/赛马23环整合工作室/程序2改装版/app"
sys.path.insert(0, APP)
import paths, phase_runner as pr, build_project_config as bpc
tmp = r"F:/赛马23环整合工作室/_整合工作区/diag_proj"
import shutil; shutil.rmtree(tmp, ignore_errors=True)
proj = os.path.join(tmp, "项目B"); os.makedirs(proj, exist_ok=True)
cfg = os.path.join(proj, "config"); bpc.build_config("通用37环", cfg); paths.set_active_project_cfg(cfg)
pr.set_call_ai(lambda role, ai_name, prompt, log_fn=print: f"【{ai_name}】产出")
logs = []
r = pr.run_book(proj, chapters=2, log_fn=lambda m: (logs.append(m), print(m)))
print("== run_book 返回:", r)
print("== 目录树 ==")
for st in ("01_规划","02_写作","03_去AI","04_审核","05_出厂"):
    base = os.path.join(proj, st)
    if not os.path.isdir(base): continue
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if os.path.isdir(p):
            fins = glob.glob(os.path.join(p, "**", "final.md"), recursive=True)
            bodies = glob.glob(os.path.join(p, "**", "*_正文.md"), recursive=True)
            print("  %s/%s: final=%d 正文=%d 子目录=%s" % (st, d, len(fins), len(bodies), sorted(os.listdir(p))[:8]))
