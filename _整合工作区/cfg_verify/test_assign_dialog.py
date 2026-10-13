# -*- coding: utf-8 -*-
"""无头测试：_Assign37Dialog 绿灯点选 / 下拉 / ≥2 校验 / 保存。"""
import os, sys, json

os.environ["QT_QPA_PLATFORM"] = "offscreen"
APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)

from PySide6.QtWidgets import QApplication, QMessageBox

app = QApplication([])

import collab_app

OUT = r"F:\赛马23环整合工作室\_整合工作区\cfg_verify\dlg_assign.json"

rings = [
    {"name": "P01_规划前约束", "mode": "human",
     "items": [{"code": "B1-1", "name": "1.0_总纲", "desc": "x"}]},
    {"name": "P02_类型平台读者卖点", "mode": "mesh", "items": []},
]
alive = {"WorkBuddy": True, "豆包": True, "QUEST": True, "kimi": True,
         "小张同学": True, "智谱WEB": True, "元宝WEB": True, "gemini": True,
         "CodeBuddy": False, "ima": False, "通义": False}
ai_names = list(alive.keys())

# 预置一条旧指派（含离线 AI ima），验证灰显保留
assigns = {"环节": {"01_规划": {"明细": {"P01_规划前约束": {
    "mode": "human", "writers": ["ima", "豆包"], "judges": ["智谱WEB"],
    "merger": "ima", "审核": "", "调整": ""}}}}}

warnings = []
QMessageBox.warning = staticmethod(lambda *a, **k: warnings.append(a[2] if len(a) > 2 else str(a)))

dlg = collab_app._Assign37Dialog("01_规划", rings, assigns, ai_names, OUT, alive=alive)
print("== 可选名单（绿灯在前，离线灰显在后）==")
print(dlg._sel_names)
w = dlg.rows["P01_规划前约束"]
print("== 旧指派回填：写手选中 ==", [n for n, b in w["writers"].items() if b.isChecked()])
print("== 旧指派回填：裁判选中 ==", [n for n, b in w["judges"].items() if b.isChecked()])
print("== 汇总下拉项 ==", [w["merger"].itemText(i) for i in range(w["merger"].count())])
print("== 汇总当前值（离线 ima 保留）==", w["merger"].currentText())

# 环1：补选到 写手2 裁判2；环2：只选 1 写手 → 应被拦截
for n in ("WorkBuddy", "QUEST"):
    w["judges"][n].setChecked(True)
w2 = dlg.rows["P02_类型平台读者卖点"]
for n in ("WorkBuddy", "豆包"):
    w2["writers"][n].setChecked(True)
    w2["judges"][n].setChecked(True)
w2["writers"]["QUEST"].setChecked(False)  # 保持 2 写手合规
w2["judges"]["kimi"].setChecked(False)    # 裁判只剩 1 → 违规

dlg._save()
print("== 触发的拦截警告 ==", warnings)
print("== 保存文件是否存在 ==", os.path.exists(OUT))
if os.path.exists(OUT):
    data = json.load(open(OUT, encoding="utf-8"))
    d1 = data["环节"]["01_规划"]["明细"]["P01_规划前约束"]
    d2 = data["环节"]["01_规划"]["明细"]["P02_类型平台读者卖点"]
    print("P01 writers/judges:", d1["writers"], "/", d1["judges"], "merger:", d1["merger"])
    print("P02 writers/judges:", d2["writers"], "/", d2["judges"])

# 再验证：全部合规时可正常保存
warnings.clear()
for n in ("豆包", "QUEST"):
    w2["judges"][n].setChecked(True)
dlg._save()
print("== 补齐裁判后再次保存：警告数 ==", len(warnings), " accept ==", dlg.result())
data = json.load(open(OUT, encoding="utf-8"))
d2 = data["环节"]["01_规划"]["明细"]["P02_类型平台读者卖点"]
print("P2 final writers/judges:", d2["writers"], "/", d2["judges"])
print("ALL TESTS DONE")
