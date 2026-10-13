# -*- coding: utf-8 -*-
"""验证：表格按连通性排序 / 下拉只含绿灯且同序 / AI指派按钮名完整不截断。"""
import io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)

from PySide6.QtWidgets import QApplication, QComboBox, QTableWidget
app = QApplication([])

import ui_base, collab_app, players as _pl
from PySide6.QtCore import Qt

# 造 8 个选手，其中 3 个绿灯（含一个长名字，验证不截断）
FAKE = [
    {"名字": "WorkBuddy", "类型": "electron", "cdp_port": 9227},
    {"名字": "CodeBuddy超长名字测试", "类型": "electron", "cdp_port": 9223},
    {"名字": "Doubao", "类型": "electron", "cdp_port": 9231},
    {"名字": "未启动甲", "类型": "web", "cdp_port": 9300},
    {"名字": "QUEST", "类型": "electron", "cdp_port": 9224},
    {"名字": "未启动乙", "类型": "web", "cdp_port": 9301},
    {"名字": "小张同学", "类型": "web", "cdp_port": 9234},
    {"名字": "gemini", "类型": "electron", "cdp_port": 9229},
]
ALIVE = {"WorkBuddy": True, "CodeBuddy超长名字测试": True, "小张同学": True}

_pl.load_players = lambda: [dict(p) for p in FAKE]      # 固定选手列表
_pl.cdp_alive = lambda port: False                      # 关掉真实探测
ui_base.load_players = _pl.load_players
ui_base.cdp_alive = _pl.cdp_alive
collab_app.players = _pl

win = ui_base.ConsoleBase.__new__(ui_base.ConsoleBase)   # 不跑 __init__ 的完整 QMainWindow
from PySide6.QtWidgets import QMainWindow
QMainWindow.__init__(win)
win.players = [dict(p) for p in FAKE]
win._last_alive = {}
win._launching = set()
win._launching_since = {}
win._dot_colors = {}
win._blink_level = 1.0
win._blink_phase = 0.0
win.table = QTableWidget(0, 5)
win.chat_ai = QComboBox()
win.summary_ai_combo = QComboBox()

# 1) 排序：绿灯在上
ordered = win._sorted_players(ALIVE)
names = [p["名字"] for p in ordered]
print("排序结果:", names)
assert names[:3] == ["WorkBuddy", "CodeBuddy超长名字测试", "小张同学"], "绿灯应在前"
assert names[3:] == ["Doubao", "未启动甲", "QUEST", "未启动乙", "gemini"], "未启动应在后且组内保序"

# 2) 绿灯名单（表格同序）
green = win._alive_names(ALIVE)
print("绿灯名单:", green)
assert green == ["WorkBuddy", "CodeBuddy超长名字测试", "小张同学"]

# 3) 下拉只含绿灯
win._fill_ai_combo(win.chat_ai, ALIVE)
items = [win.chat_ai.itemText(i) for i in range(win.chat_ai.count())]
print("下拉内容:", items)
assert items == green, "下拉应只含绿灯且同序"

# 绿灯清空时禁用
win._fill_ai_combo(win.summary_ai_combo, {})
print("无绿灯时 count=%d enabled=%s" % (win.summary_ai_combo.count(), win.summary_ai_combo.isEnabled()))
assert win.summary_ai_combo.count() == 0 and not win.summary_ai_combo.isEnabled()

# 4) AI指派对话框：只显示绿灯 + 名字完整（按钮宽度足够）
mods = [{"stage": "01_规划", "count": 23, "sample": "P01、P02"}]
dlg = collab_app._AssignModuleDialog(mods, {}, green, ALIVE, r"F:\tmp_assign.json")
print("对话框绿灯顺序:", dlg.green)
assert dlg.green == green
btns = dlg.rows["01_规划"]["writers"]
print("按钮清单:", list(btns))
assert set(btns) == set(green), "按钮只应是绿灯 AI"
for n, b in btns.items():
    w = b.minimumWidth()
    need = sum(15 if ("\u2e80" <= c <= "\u9fff") else 9 for c in n) + 30
    print("  %-22s 按钮宽=%d 需要≈%d %s" % (n, w, need, "OK" if w >= need else "偏窄!"))
    assert w >= need, f"{n} 按钮宽度不足，名字会被截断"
assert dlg.rows["01_规划"]["merger"].count() == len(green) + 1  # +（不设）

print("\n=== ALL PASS ===")