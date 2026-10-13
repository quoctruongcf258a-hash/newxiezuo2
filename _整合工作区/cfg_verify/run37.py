# -*- coding: utf-8 -*-
"""Clean headless verification of the 37-ring engine against the generated
per-project config (疯骨56). Uses the built-in pseudo-AI (no network, no recursion).
"""
import os
import sys
import json

APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)

import paths
import phase_runner

CFG = r"F:\赛马23环整合工作室\_整合工作区\cfg_verify\config"
WS = r"F:\赛马23环整合工作室\_整合工作区\cfg_verify\ws"

paths.set_active_project_cfg(CFG)   # 关键：让引擎读取按项目配置
print("get_cfg_rules_dir ->", paths.get_cfg_rules_dir())

logs = []
phase_runner.run_phase("01_规划", log_fn=logs.append, project_dir=WS)

phase_dir = os.path.join(WS, "01_规划")

# 统计产出
final_dirs = []
draft = review = 0
for root, dirs, files in os.walk(phase_dir):
    rel = os.path.relpath(root, phase_dir)
    if "final.md" in files:
        final_dirs.append(rel)
    draft += sum(1 for f in files if f.startswith("draft_") and f.endswith(".md"))
    review += sum(1 for f in files if f.startswith("review_") and f.endswith(".md"))

# 期望的 56 子项（与 phases.json 比对）
phases = json.load(open(os.path.join(CFG, "phases.json"), encoding="utf-8"))
expected = []
for r in phases["环节"]["01_规划"]:
    for it in r.get("items", []):
        expected.append(f"{r['name']}__{it['code']}")

missing = [e for e in expected if e not in final_dirs]
extra = [d for d in final_dirs if d not in expected]

print("规划环数:", len(phases['环节']['01_规划']))
print("期望子项数:", len(expected))
print("实际 final.md 数:", len(final_dirs))
print("draft_ 文件数(写手):", draft)
print("review_ 文件数(盲审):", review)
print("汇总(final)数: ", len(final_dirs))
print("缺失子项:", missing)
print("多余子项:", extra)
print("RESULT:", "PASS" if (len(final_dirs) == 56 and not missing and not extra) else "FAIL")
