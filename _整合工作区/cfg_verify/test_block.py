# -*- coding: utf-8 -*-
import os, sys, json
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, r"F:/赛马23环整合工作室/程序2改装版/app")
from PySide6.QtWidgets import QApplication, QMessageBox
app = QApplication([])
import collab_app
OUT = r"F:/赛马23环整合工作室/_整合工作区/cfg_verify/dlg_block.json"
rings = [{"name": "R1", "mode": "mesh", "items": []}]
alive = {"A": True, "B": True, "C": True}
warns = []
QMessageBox.warning = staticmethod(lambda *a, **k: warns.append(a[2]))
dlg = collab_app._Assign37Dialog("01_规划", rings, {"环节": {}}, list(alive), OUT, alive=alive)
w = dlg.rows["R1"]
for n in ("A", "B"):
    w["writers"][n].setChecked(True)
w["judges"]["A"].setChecked(True)   # 只 1 个裁判 → 应拦截
dlg._save()
print("warnings:", len(warns), "| file_exists:", os.path.exists(OUT))
print(warns[0][:60] if warns else "NO WARN")
