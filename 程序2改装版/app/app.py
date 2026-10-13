import os
import sys, os, json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui_main import MainWindow
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

DARK_QSS = """
QWidget { background-color: #1e1e1e; color: #d4d4d4; font-family: "Microsoft YaHei"; font-size: 12px; }
QMainWindow { background-color: #1e1e1e; }
QGroupBox { background-color: #252526; border: 1px solid #3c3c3c; border-radius: 4px; margin-top: 8px; padding-top: 8px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; color: #4ec9b0; }
QTableWidget { background-color: #1e1e1e; alternate-background-color: #252526; gridline-color: #3c3c3c; selection-background-color: #094771; selection-color: #ffffff; }
QHeaderView::section { background-color: #2d2d30; color: #d4d4d4; border: 1px solid #3c3c3c; padding: 4px; }
QTableCornerButton::section { background-color: #2d2d30; border: none; }
QHeaderView::section:vertical { background-color: #2d2d30; color: #d4d4d4; border: 1px solid #3c3c3c; }
QPushButton { background-color: #0e639c; color: #ffffff; border: none; padding: 6px 14px; border-radius: 3px; }
QPushButton:hover { background-color: #1177bb; }
QPushButton:pressed { background-color: #094771; }
QPushButton:disabled { background-color: #3c3c3c; color: #808080; }
QComboBox, QLineEdit { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555; padding: 4px; border-radius: 3px; }
QComboBox QAbstractItemView { background-color: #252526; color: #d4d4d4; selection-background-color: #094771; }
QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #3c3c3c; }
QCheckBox { color: #d4d4d4; }
QLabel { color: #d4d4d4; }
QScrollBar:vertical { background: #1e1e1e; width: 12px; }
QScrollBar::handle:vertical { background: #424242; border-radius: 6px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""

LAYOUT = paths.join("windows-use", "layout.json")

def load_ui_pos():
    if not os.path.exists(LAYOUT): return None
    try:
        with open(LAYOUT, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d.get("__UI__")
    except: return None

def save_ui_pos(w):
    try:
        if os.path.exists(LAYOUT):
            with open(LAYOUT, "r", encoding="utf-8") as f:
                d = json.load(f)
        else:
            d = {}
        geo = w.geometry()
        d["__UI__"] = {
            "title": w.windowTitle(),
            "x": geo.x(), "y": geo.y(),
            "width": geo.width(), "height": geo.height(),
        }
        with open(LAYOUT, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("save_ui_pos err:", e)


class AppWindow(MainWindow):
    def showEvent(self, e):
        super().showEvent(e)
        if getattr(self, "_first_show_done", False): return
        self._first_show_done = True
        saved = load_ui_pos()
        if saved and saved.get("x") is not None:
            self.setGeometry(saved["x"], saved["y"], saved["width"], saved["height"])
            return
        # 拿显示器工作区（排除任务栏）
        try:
            import win32api
            mon = win32api.MonitorFromPoint((0, 0))
            work = win32api.GetMonitorInfo(mon)["Work"]
            left, top, right, bottom = work
        except Exception:
            scr = QApplication.primaryScreen().availableGeometry()
            left, top, right, bottom = scr.left(), scr.top(), scr.right()+1, scr.bottom()+1
        ww = 401
        hh = 1016
        xx = right - ww
        yy = top
        self.setGeometry(xx, yy, ww, hh)
        # showEvent 里已 show，frame 已知
        fg = self.frameGeometry(); gg = self.geometry()
        extra_h = fg.height() - gg.height()   # 标题栏 + 下边框
        title_h = extra_h - 8                 # 估计下边框 8
        # 标题栏顶出屏幕，底部正好贴任务栏顶
        from PySide6.QtCore import QTimer
        from PySide6.QtCore import QTimer

    def closeEvent(self, e):
        save_ui_pos(self)
        super().closeEvent(e)


app = QApplication(sys.argv)
app.setStyleSheet(DARK_QSS)
w = AppWindow()
w.show()
sys.exit(app.exec())
