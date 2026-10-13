"""ui_base.py — 赛马控制台 / 协同写作控制台 的公共底座。

统一成熟的 IDE 风排版：
  · 顶部工具栏：启动全部 / 停止 / 刷新 / 重启 / 打开工作区 / 打开产出文件夹 / dry-run 开关
  · 左侧可停靠「选手」栏：启动、状态、CDP、类型、进程、路径 + 右键菜单
  · 中央标签页：由子类填充（流水线 / 监控 / 协同写作 / 脚本 …）
  · 底部可停靠「日志 · 单聊」栏：只读日志 + 单聊发送
  · 统一深色主题（VS Code 风）

子类只需：
  - 调用 super().__init__(标题)
  - 向 self.tab 添加自己的标签页
  - 按需覆盖钩子：add_player / open_result_dir（产出文件夹） / open_workspace_dir / on_stop
公共的协同写作标签页由 build_collab_tab() 提供（环节编排 + AI 指派 + 放行/执行控制）。

不修改 core/、mix_send.py、ai_apps.json。
"""
import os
import sys
import time
import math
import psutil

import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.APP_ROOT)

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
                               QDockWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QLabel, QCheckBox, QComboBox, QLineEdit,
                               QTextEdit, QGroupBox, QMenu, QMessageBox, QTabWidget,
                               QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QColor, QFont

from players import load_players, save_players, is_running, launch, kill, cdp_alive
from pipeline_runner import set_dry_run as pr_set_dry_run
import stage_board as sb


class _StatusProbeWorker(QThread):
    """后台探测各选手 CDP 连通性，避免在主线程逐个做 socket 连接导致界面卡顿。
    每约 2 秒探测一次，发出 {名字: 是否连通} 字典，由 GUI 线程套用更新表格。"""
    result = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False

    def run(self):
        import time as _t
        while not self._stop:
            try:
                alive = {}
                for p in load_players():
                    port = p.get("cdp_port")
                    alive[p.get("名字")] = bool(port and cdp_alive(port))
                self.result.emit(alive)
            except Exception:
                pass
            # 以 0.1s 为步长睡眠，便于被快速 stop
            for _ in range(20):
                if self._stop:
                    break
                _t.sleep(0.1)

    def stop(self):
        self._stop = True

from stage_board import StageBoard
from assign_panel import AssignPanel
import collab_exec


DOT_SIZE = 17   # 状态圆点边长（较原先 20 缩小 3）


def _dot_qss(color, size=DOT_SIZE, level=1.0):
    """生成带立体高光（径向渐变 + 暗化描边）的圆点样式。
    level=1 最亮，越小越暗，用于平滑渐变闪烁（不再是硬亮/暗两相）。"""
    h = color.lstrip("#")
    r0, g0, b0 = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r0, g0, b0 = int(r0 * level), int(g0 * level), int(b0 * level)
    hi_alpha = int(235 * level)
    hi = f"rgba(255,255,255,{hi_alpha})"
    stop_mid = 0.28 + 0.10 * (1 - level)
    base = "#%02x%02x%02x" % (r0, g0, b0)
    dark = "#%02x%02x%02x" % (int(r0 * 0.55), int(g0 * 0.55), int(b0 * 0.55))
    return (
        f"QPushButton{{border-radius:{size // 2}px;"
        f"background:qradialgradient(cx:0.32, cy:0.28, radius:0.88,"
        f" stop:0 {hi}, stop:{stop_mid:.2f} {base}, stop:1 {dark});"
        f"border:1px solid {dark};}}"
        "QPushButton:pressed{background:#ffffff;}"
    )


# --------------------------------------------------------------------------- 主题
DARK_QSS = """
QMainWindow, QDockWidget, QWidget { background-color:#1e1e1e; color:#d4d4d4; }
QToolBar { background:#252526; border:none; spacing:6px; padding:4px 6px; }
QToolBar QToolButton, QToolBar QPushButton {
    color:#d4d4d4; background:#333333; border:1px solid #3c3c3c;
    border-radius:4px; padding:4px 10px;
}
QToolBar QPushButton:hover, QToolBar QToolButton:hover { background:#3e3e42; }
QDockWidget { background:#1e1e1e; border:1px solid #2d2d30; }
QDockWidget::title { background:#2d2d30; padding:5px 8px; color:#d4d4d4;
    subcontrol-origin:margin; subcontrol-position:top left; }
QGroupBox { background:#252526; border:1px solid #3c3c3c; border-radius:6px;
    margin-top:16px; padding:10px; }
QGroupBox::title { subcontrol-origin:margin; left:10px; color:#569cd6;
    subcontrol-position:top left; }
QTabWidget::pane { border:1px solid #3c3c3c; top:-1px; }
QTabBar::tab { background:#2d2d30; color:#d4d4d4; padding:7px 16px;
    border:1px solid #3c3c3c; border-bottom:none;
    border-top-left-radius:5px; border-top-right-radius:5px; }
QTabBar::tab:selected { background:#1e1e1e; color:#ffffff;
    border-bottom:2px solid #569cd6; }
QPushButton { background:#333333; color:#d4d4d4; border:1px solid #3c3c3c;
    border-radius:4px; padding:5px 10px; }
QPushButton:hover { background:#3e3e42; }
QPushButton:disabled { color:#666; background:#2a2a2a; }
QTableWidget { background:#1e1e1e; gridline-color:#3c3c3c; border:1px solid #3c3c3c; }
QHeaderView::section { background:#2d2d30; color:#d4d4d4; border:1px solid #3c3c3c;
    padding:4px; }
QTextEdit, QLineEdit, QComboBox { background:#1e1e1e; color:#d4d4d4;
    border:1px solid #3c3c3c; border-radius:4px; padding:4px; }
QComboBox QAbstractItemView { background:#1e1e1e; color:#d4d4d4;
    selection-background-color:#094771; }
QLabel { color:#d4d4d4; }
QCheckBox { color:#d4d4d4; spacing:4px; }
QMenu { background:#252526; color:#d4d4d4; border:1px solid #3c3c3c; }
QMenu::item:selected { background:#094771; }
QScrollBar:vertical { background:#1e1e1e; width:10px; }
QScrollBar::handle:vertical { background:#3c3c3c; border-radius:5px; }
QStatusBar { background:#007acc; color:#fff; }
"""


def apply_dark(app):
    app.setStyleSheet(DARK_QSS)


class ConsoleBase(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1240, 840)
        self.players = load_players()

        self._build_toolbar()
        self._build_player_dock()
        self._build_log_dock()

        self.tab = QTabWidget()
        self.setCentralWidget(self.tab)

        # 启动圆点：黄=启动中（点击后直到 CDP 就绪或超时）
        self._launching = set()
        self._launching_since = {}
        self._dot_colors = {}
        self._blink_level = 1.0    # 圆点渐变亮度（1 最亮，0~1 渐暗）
        self._blink_phase = 0.0    # 渐变相位（秒）
        self._blink_timer = QTimer()
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blink_timer.start(50)   # 50ms 步进，平滑渐变闪烁（5 秒一周期）
        # 连通性探测放到后台线程，避免主线程被逐个 socket 连接阻塞导致卡顿
        self._last_alive = {}
        self._probe = _StatusProbeWorker(self)
        self._probe.result.connect(self.refresh_status)
        self._probe.start()
        self.rebuild_table()

    # -------------------------------------------------------------- 日志/时间
    def log_line(self, s):
        self.log.append(f"[{time.strftime('%H:%M:%S')}] {s}")

    # -------------------------------------------------------------- 工具栏
    def _build_toolbar(self):
        tb = QToolBar("主工具栏")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addToolBar(tb)

        self.a_all = tb.addAction("▶ 启动全部")
        self.a_stop = tb.addAction("⏹ 停止")
        tb.addSeparator()
        self.a_refresh = tb.addAction("🔄 刷新")
        self.a_restart = tb.addAction("🔄 重启")
        tb.addSeparator()
        self.a_open_ws = tb.addAction("📂 打开工作区")
        self.a_open_out = tb.addAction("📂 打开产出文件夹")
        tb.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)
        self.lbl_mode = QLabel("真实模式")
        self.lbl_mode.setStyleSheet("color:#888; padding-right:8px;")
        tb.addWidget(self.lbl_mode)

        self.cb_dry = QCheckBox("dry-run")
        self.cb_dry.setChecked(False)
        self.cb_dry.stateChanged.connect(self._on_dry)
        tb.addWidget(self.cb_dry)

        self.a_all.triggered.connect(self.launch_all)
        self.a_stop.triggered.connect(self.on_stop)
        self.a_refresh.triggered.connect(self.refresh_all)
        self.a_restart.triggered.connect(self.restart_app)
        self.a_open_ws.triggered.connect(self.open_workspace_dir)
        self.a_open_out.triggered.connect(self.open_result_dir)

    def _on_dry(self, state):
        pr_set_dry_run(state == 2)
        self.lbl_mode.setText("模拟模式" if state == 2 else "真实模式")
        self.on_dry(state)

    def on_dry(self, state):
        """子类钩子：切换 dry 时同步其它模块（如 collab_exec）。"""

    # -------------------------------------------------------------- 选手停靠栏
    def _build_player_dock(self):
        dock = QDockWidget("选手（AI 窗口管理）", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        w = QWidget()
        v = QVBoxLayout(w)

        bar = QHBoxLayout()
        self.b_add = QPushButton("➕ 添加AI平台")
        bar.addWidget(self.b_add)
        v.addLayout(bar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["选择", "启动", "名字", "类型", "连通性"])
        self.table.verticalHeader().setVisible(False)  # 行号列改成复选框列
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        # 原状态列(50)宽度合并给名字列：60+50=110
        for i, wd in enumerate([30, 48, 110, 60, 70]):   # 启动列 +20，连通性列 −20
            self.table.setColumnWidth(i, wd)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_menu)
        v.addWidget(self.table)
        self.player_checks = []
        self.player_start_btns = []

        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.player_dock = dock  # 暴露给子类（如 CollabApp 在选手表下方挂运行/日志）

        self.b_add.clicked.connect(self.add_player)

    # -------------------------------------------------------------- 日志/单聊栏
    def _build_log_dock(self):
        dock = QDockWidget("日志 / 单聊", self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        w = QWidget()
        v = QVBoxLayout(w)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 9))
        self.log.setMinimumHeight(120)
        v.addWidget(self.log)

        chat = QHBoxLayout()
        chat.addWidget(QLabel("单聊:"))
        self.chat_ai = QComboBox()
        self.chat_ai.setMinimumWidth(140)
        self.chat_in = QLineEdit()
        self.chat_in.setPlaceholderText("输入消息，回车或点发送…")
        self.chat_btn = QPushButton("发送")
        self.chat_btn.setMaximumWidth(80)
        chat.addWidget(self.chat_ai)
        chat.addWidget(self.chat_in)
        chat.addWidget(self.chat_btn)
        v.addLayout(chat)

        dock.setWidget(w)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.log_dock = dock  # 暴露给子类（如 CollabApp 需要收起）

        self.chat_btn.clicked.connect(self.quick_send)
        self.chat_in.returnPressed.connect(self.quick_send)

    # -------------------------------------------------------------- 选手表
    def _sorted_players(self, alive_dict):
        """已启动（绿灯）在上、未启动在下；同组内保持配置里的原有顺序。"""
        ps = list(getattr(self, "players", []) or [])
        return sorted(ps, key=lambda p: 0 if alive_dict.get(p.get("名字")) else 1)

    def _alive_names(self, alive_dict=None):
        """当前已启动（绿灯）的 AI 名字，顺序与表格一致。"""
        alive_dict = alive_dict if alive_dict is not None else getattr(self, "_last_alive", {})
        return [p.get("名字") for p in self._sorted_players(alive_dict)
                if alive_dict.get(p.get("名字")) and p.get("名字")]

    def _fill_ai_combo(self, combo, alive_dict):
        """下拉只列已启动（绿灯）的 AI，顺序与选手表一致。"""
        if combo is None:
            return
        cur = combo.currentText()
        names = self._alive_names(alive_dict)
        combo.blockSignals(True)
        combo.clear()
        for n in names:
            combo.addItem(n)
        i = combo.findText(cur)
        combo.setCurrentIndex(i if i >= 0 else (0 if names else -1))
        combo.setEnabled(bool(names))
        combo.setToolTip("只显示已启动（绿灯）的 AI" if names else "当前没有已启动的 AI，请先在选手栏启动")
        combo.blockSignals(False)

    def rebuild_table(self):
        self.players = load_players()
        # 保持"已启动在上"的排序
        self.players = self._sorted_players(getattr(self, "_last_alive", {}))
        self.table.setRowCount(len(self.players))
        if hasattr(self, "chat_ai"):
            self._fill_ai_combo(self.chat_ai, getattr(self, "_last_alive", {}))
        if hasattr(self, "summary_ai_combo"):
            self._fill_ai_combo(self.summary_ai_combo, getattr(self, "_last_alive", {}))
        self.player_checks = []
        self.player_start_btns = []
        for i, p in enumerate(self.players):
            chk = QCheckBox()
            chk.setChecked(True)
            self.table.setCellWidget(i, 0, chk)
            self.player_checks.append(chk)

            start_btn = QPushButton("")
            start_btn.setFixedSize(DOT_SIZE, DOT_SIZE)
            start_btn.setToolTip(f"启动「{p.get('名字', '?')}」")
            start_btn.clicked.connect(lambda _, idx=i: self.launch_one(idx))
            # 包一层容器让圆点在单元格里居中
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(0)
            cl.addWidget(start_btn)
            cl.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(i, 1, cell)
            self.player_start_btns.append(start_btn)

            for j, k in enumerate(["名字", "类型", "CDP"]):
                val = p.get(k, "-")
                if k == "类型":
                    val = {"electron": "本地版", "web": "网页版"}.get(val, val)
                it = QTableWidgetItem(str(val))
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)   # 禁止双击/点选后改名
                self.table.setItem(i, j + 2, it)
        self.refresh_status()

    def refresh_status(self, alive_dict=None):
        # alive_dict 来自后台探测 worker（名字->是否连通）；未提供时使用最近一次缓存
        if alive_dict is None:
            alive_dict = getattr(self, "_last_alive", {})
        else:
            self._last_alive = alive_dict
            # 连通性变化 → 重排（已启动在上）并同步下拉，只在顺序真的变了时才重建表格
            ordered = self._sorted_players(alive_dict)
            if [p.get("名字") for p in ordered] != [p.get("名字") for p in self.players]:
                self.rebuild_table()
                self._sync_ai_combos(alive_dict)
                return
        for combo_name in ("chat_ai", "summary_ai_combo"):
            self._fill_ai_combo(getattr(self, combo_name, None), alive_dict)
        for i, p in enumerate(self.players):
            name = p.get("名字")
            port = p.get("cdp_port")
            alive = bool(alive_dict.get(name))

            it2 = self.table.item(i, 4)
            if it2 is not None:
                if not port:
                    it2.setText("-")
                    it2.setForeground(QColor("gray"))
                elif alive:
                    it2.setText(f"✅ {port}")
                    it2.setForeground(QColor("green"))
                else:
                    it2.setText(f"❌ {port}")
                    it2.setForeground(QColor("red"))

            if i < len(self.player_start_btns):
                btn = self.player_start_btns[i]
                import time as _t
                # 启动中超时（60s）未就绪则退回未启动
                if i in self._launching and not alive and \
                        _t.time() - self._launching_since.get(i, 0) > 60:
                    self._launching.discard(i)
                if alive:
                    color, tip, enabled = "#1e8e3e", "已启动", False
                    self._launching.discard(i)
                elif i in self._launching:
                    color, tip, enabled = "#f9ab00", "启动中…", False
                else:
                    color, tip, enabled = "#d93025", "未启动（点击启动）", True
                btn.setText("")
                self._dot_colors[i] = color
                btn.setStyleSheet(_dot_qss(
                    color, DOT_SIZE,
                    level=self._blink_level if color != "#d93025" else 1.0))
                btn.setEnabled(enabled)
                btn.setToolTip(f"{name} · {tip}")

            if i < len(self.player_checks):
                self.player_checks[i].setChecked(not alive)
                self.player_checks[i].setEnabled(not alive)

    def _sync_ai_combos(self, alive_dict=None):
        """子类钩子：连通性/排序变化后，把下拉与指派面板同步成"只含绿灯、与表格同序"。
        基类只处理自带下拉；CollabApp 覆写以联动 stage_panels。"""
        return

    def _toggle_blink(self):
        """渐变闪烁：以 5 秒为周期平滑改变启动圆点亮度（亮↔暗），非硬切换。"""
        self._blink_phase += 0.05
        period = 5.0
        w = (self._blink_phase % period) / period
        self._blink_level = 0.5 + 0.5 * math.sin(2 * math.pi * w)
        self._paint_player_dots()

    def _paint_player_dots(self):
        """按缓存的圆点颜色重绘启动列圆点（渐变闪烁）。"""
        for i, btn in enumerate(getattr(self, "player_start_btns", [])):
            color = self._dot_colors.get(i)
            if color:
                # 红点（未启动）不闪烁，仅绿/黄渐变
                lvl = self._blink_level if color != "#d93025" else 1.0
                btn.setStyleSheet(_dot_qss(color, DOT_SIZE, level=lvl))

    def _cdp_dead_but_running(self, p):
        """本地版：软件进程在跑、但 CDP 调试端口没开 → 说明是普通方式打开的，
        再点启动只会转给旧实例，端口永远开不了。返回 True 时应阻止启动并提示。"""
        if p.get("类型") != "electron" or not p.get("cdp_port"):
            return False
        return is_running(p) and not cdp_alive(p.get("cdp_port"))

    def launch_one(self, idx):
        p = self.players[idx]
        import time as _t
        if self._cdp_dead_but_running(p):
            self.log_line(f"⛔ {p['名字']} 已在运行但调试端口 {p.get('cdp_port')} 未开"
                          f"（普通方式打开的）。请先完全退出该软件（含托盘/后台），"
                          f"再点启动按钮，让它带 --remote-debugging-port 参数启动。")
            return
        self._launching.add(idx)
        self._launching_since[idx] = _t.time()
        if idx < len(self.player_start_btns):
            self.player_start_btns[idx].setEnabled(False)
        # 后台探测 worker 每约 2 秒刷新连通性，启动中圆点会自动变绿，无需额外定时器
        r = launch(p)
        self.log_line(f"🚀 {p['名字']} → {r}")
        self.refresh_status()

    def launch_all(self):
        checks = getattr(self, "player_checks", [])
        for i, p in enumerate(self.players):
            if i < len(checks) and checks[i].isChecked():
                if self._cdp_dead_but_running(p):
                    self.log_line(f"⛔ {p['名字']} 已在运行但调试端口 {p.get('cdp_port')} 未开，"
                                  f"请先完全退出后再启动。")
                    continue
                r = launch(p)
                self.log_line(f"🚀 {p['名字']} → {r}")
        self.refresh_status()

    def kill_all(self):
        for p in self.players:
            kill(p)
        self.log_line("⏹ 已关闭全部选手")
        self.refresh_status()

    def on_table_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0 or row >= len(self.players):
            return
        p = self.players[row]
        name = p.get("名字", "?")
        menu = QMenu(self)
        act_open = menu.addAction(f"▶ 启动「{name}」")
        act_kill = menu.addAction(f"⏹ 关闭「{name}」")
        act_edit = menu.addAction(f"⚙ 修改配置「{name}」")
        menu.addSeparator()
        act_del = menu.addAction(f"🗑 删除「{name}」")
        act = menu.exec(self.table.viewport().mapToGlobal(pos))
        if act == act_open:
            self.launch_one(row)
        elif act == act_kill:
            try:
                kill(p)
                self.log_line(f"⏹ 已关闭: {name}")
            except Exception as e:
                self.log_line(f"❌ 关闭失败: {e}")
            self.refresh_status()
        elif act == act_edit:
            self.edit_player(name)
        elif act == act_del:
            self.delete_player(name)

    def delete_player(self, name):
        r = QMessageBox.question(self, "确认删除",
                                 f"确定删除选手「{name}」？\n（仅从配置移除，不关闭进程）")
        if r != QMessageBox.Yes:
            return
        ps = [x for x in load_players() if x.get("名字") != name]
        save_players(ps)
        self.rebuild_table()
        self.log_line(f"🗑 已删除: {name}")

    # -------------------------------------------------------------- 选手管理
    def _player_wizard(self, existing=None):
        """步骤式添加 AI 选手（5 步向导）：名字 / 类型 / 路径 / URL / 进程 + CDP 端口。"""
        from PySide6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                                       QLabel, QLineEdit, QRadioButton, QPushButton,
                                       QListWidget, QListWidgetItem, QFileDialog)
        from PySide6.QtCore import Qt as _Qt

        PROC_CN = {
            "msedge": "Microsoft Edge", "chrome": "Google Chrome",
            "firefox": "Firefox", "brave": "Brave", "opera": "Opera",
            "vivaldi": "Vivaldi", "chromium": "Chromium",
            "codebuddy cn": "CodeBuddy", "qodercn": "QUEST (Qoder)",
            "trae solo cn": "TraeWork", "qianwen": "通义千问",
            "workbuddy": "WorkBuddy", "zcode": "ZCode", "doubao": "豆包",
            "wechat": "微信", "qq": "QQ", "dingtalk": "钉钉", "feishu": "飞书",
            "cursor": "Cursor", "code": "VS Code", "notepad": "记事本",
        }
        BROWSERS = {"msedge", "chrome", "firefox", "brave", "opera",
                    "vivaldi", "chromium"}

        def cn(n):
            return PROC_CN.get(n.lower(), "")

        class Wizard(QWizard):
            def __init__(self, existing=None):
                super().__init__()
                self.setWindowTitle("编辑 AI 选手" if existing else "添加 AI 选手")
                self.resize(660, 480)
                self.p1 = QWizardPage()
                self.p1.setTitle("步骤 1/5 · AI 名字")
                self.p1.setSubTitle("自定义名字，无需与进程名一致")
                l = QVBoxLayout(self.p1)
                self.in_name = QLineEdit()
                self.in_name.setPlaceholderText("给这个 AI 起个名字")
                l.addWidget(QLabel("名字："))
                l.addWidget(self.in_name)

                self.p2 = QWizardPage()
                self.p2.setTitle("步骤 2/5 · 类型")
                self.p2.setSubTitle("本地端=桌面应用；云端=网页（浏览器 + CDP）")
                l = QVBoxLayout(self.p2)
                self.rb_local = QRadioButton("本地端（桌面 App / Electron）")
                self.rb_cloud = QRadioButton("云端（网页，用浏览器打开并开 CDP）")
                self.rb_local.setChecked(True)
                l.addWidget(self.rb_local)
                l.addWidget(self.rb_cloud)

                self.p3 = QWizardPage()
                self.p3.setTitle("步骤 3/5 · 本地应用路径")
                self.p3.setSubTitle("选择 .exe 的完整路径")
                l = QVBoxLayout(self.p3)
                h = QHBoxLayout()
                self.in_exe = QLineEdit()
                btn = QPushButton("浏览...")
                h.addWidget(self.in_exe)
                h.addWidget(btn)
                l.addWidget(QLabel("EXE 完整路径："))
                l.addLayout(h)
                btn.clicked.connect(self._browse)

                self.p4 = QWizardPage()
                self.p4.setTitle("步骤 4/5 · 网站 URL")
                self.p4.setSubTitle("填入完整网址（含 https://）")
                l = QVBoxLayout(self.p4)
                self.in_url = QLineEdit()
                self.in_url.setPlaceholderText("https://...")
                l.addWidget(QLabel("URL："))
                l.addWidget(self.in_url)

                self.p5 = QWizardPage()
                self.p5.setTitle("步骤 5/5 · 进程 + CDP 端口")
                self.p5.setSubTitle("点『扫描』从列表选择（本地端=全部；云端=仅浏览器）")
                l = QVBoxLayout(self.p5)
                self.lbl_proc = QLabel("进程名：")
                self.in_proc = QLineEdit()
                h1 = QHBoxLayout()
                h1.addWidget(self.lbl_proc)
                h1.addWidget(self.in_proc)
                l.addLayout(h1)
                self.btn_scan = QPushButton("🔍 扫描当前进程")
                l.addWidget(self.btn_scan)
                self.lst = QListWidget()
                self.lst.setVisible(False)
                self.lst.setMaximumHeight(170)
                l.addWidget(self.lst)
                self.lbl_cdp = QLabel("")
                self.lbl_cdp.setStyleSheet("color:#00e5ff; font-size:12px;")
                l.addWidget(self.lbl_cdp)
                h2 = QHBoxLayout()
                h2.addWidget(QLabel("CDP 端口："))
                self.in_port = QLineEdit()
                self.in_port.setPlaceholderText("自动分配（可手改）")
                h2.addWidget(self.in_port)
                l.addLayout(h2)
                self._all_procs = []          # 最近一次扫描到的全部进程名
                self._cdp_cache = {}          # 进程名 -> 检测到的监听端口列表
                self.btn_scan.clicked.connect(self._scan)
                self.in_proc.textChanged.connect(self._filter_procs)
                self.lst.itemClicked.connect(self._pick)
                self.addPage(self.p1)
                self.addPage(self.p2)
                self.addPage(self.p3)
                self.addPage(self.p4)
                self.addPage(self.p5)

                if existing:
                    self.in_name.setText(existing.get("名字", ""))
                    if existing.get("类型") == "web":
                        self.rb_cloud.setChecked(True)
                    else:
                        self.rb_local.setChecked(True)
                    self.in_exe.setText(existing.get("exe", ""))
                    self.in_url.setText(existing.get("url", ""))
                    self.in_proc.setText(existing.get("进程名", ""))
                    pt = existing.get("cdp_port")
                    self.in_port.setText(str(pt) if pt is not None else "")

            def _browse(self):
                fn, _ = QFileDialog.getOpenFileName(self, "选择 EXE", "", "可执行文件 (*.exe)")
                if fn:
                    self.in_exe.setText(fn)

            def _next_port(self, start=9229):
                try:
                    cfg = load_players()
                except Exception:
                    cfg = []
                used = {e.get("cdp_port") for e in cfg if isinstance(e.get("cdp_port"), int)}
                port = start
                while port in used:
                    port += 1
                return port

            def _scan(self):
                is_web = not self.rb_local.isChecked()
                names = set()
                for pr in psutil.process_iter(['name']):
                    n = (pr.info.get('name') or '').strip()
                    if n.lower().endswith('.exe'):
                        n = n[:-4]
                    if not n:
                        continue
                    if is_web and n.lower() not in BROWSERS:
                        continue
                    names.add(n)
                self._all_procs = sorted(names, key=lambda x: x.lower())
                self._cdp_cache.clear()
                self._filter_procs()

            def _filter_procs(self):
                """按『进程名』输入实时过滤+按相似度排序：精确=0、前缀=1、包含=2、模糊=3。"""
                import difflib
                self.lst.clear()
                self.lst.setVisible(True)
                if not self._all_procs:
                    if self._all_procs is not None:
                        self.lst.addItem(QListWidgetItem("（未找到进程，点『扫描』刷新）"))
                    return
                kw = self.in_proc.text().strip().lower().removesuffix(".exe")
                def rank(n):
                    low = n.lower()
                    if kw and low == kw: return (0, 0.0)
                    if kw and low.startswith(kw): return (1, 0.0)
                    if kw and kw in low: return (2, 0.0)
                    if kw:
                        return (3, -difflib.SequenceMatcher(None, kw, low).ratio())
                    return (4, 0.0)
                shown = self._all_procs
                if kw:
                    shown = sorted(self._all_procs, key=rank)[:40]
                if not shown:
                    self.lst.addItem(QListWidgetItem("（无相近进程，点『扫描』刷新）"))
                    return
                top = None
                for n in shown:
                    z = cn(n)
                    disp = f"{z}  （{n}）" if z else n
                    it = QListWidgetItem(disp)
                    it.setData(_Qt.UserRole, n)
                    self.lst.addItem(it)
                    if top is None:
                        top = it
                if top is not None:
                    self.lst.setCurrentItem(top)   # 最相近的直接高亮
                    if kw and top.data(_Qt.UserRole).lower() == kw:
                        self._apply_proc(top.data(_Qt.UserRole))   # 精确命中：自动填端口

            def _detect_cdp_ports(self, name):
                """探测该进程名当前监听中的端口（netstat 按_PID 匹配）。
                优先返回 9222-9299 常用 CDP 段；无则返回全部监听端口。"""
                if name in self._cdp_cache:
                    return self._cdp_cache[name]
                import subprocess as _sp
                key = name.lower().removesuffix(".exe")
                pids = set()
                for pr in psutil.process_iter(['name']):
                    if (pr.info.get('name') or '').lower().startswith(key):
                        pids.add(pr.pid)
                ports = []
                if pids:
                    try:
                        out = _sp.run(["netstat", "-ano"], capture_output=True,
                                      text=True, timeout=8).stdout
                    except Exception:
                        out = ""
                    for line in out.splitlines():
                        parts = line.split()
                        if len(parts) >= 5 and parts[3].upper() == "LISTENING":
                            try:
                                pid = int(parts[-1]); port = int(parts[1].rsplit(":", 1)[-1])
                            except Exception:
                                continue
                            if pid in pids and port not in ports:
                                ports.append(port)
                cdp = [p for p in ports if 9222 <= p <= 9299]
                res = cdp or ports
                self._cdp_cache[name] = res
                return res

            def _apply_proc(self, name):
                """选中/精确命中进程后：自动回填 CDP 端口（配置 > 实测监听 > 自动分配）。"""
                self.lbl_cdp.setText("")
                is_web = not self.rb_local.isChecked()
                if is_web:
                    self.in_port.setText(str(self._next_port(9222)))
                    return
                try:
                    cfg = load_players()
                except Exception:
                    cfg = []
                for e in cfg:
                    if (e.get("进程名") or "").lower() == name.lower() and e.get("cdp_port"):
                        self.in_port.setText(str(e["cdp_port"]))
                        self.lbl_cdp.setText(f"🔎 {name}：使用已配置的 CDP 端口 {e['cdp_port']}")
                        return
                ports = self._detect_cdp_ports(name)
                if ports:
                    self.in_port.setText(str(ports[0]))
                    extra = f"（全部监听：{', '.join(map(str, ports))}）" if len(ports) > 1 else ""
                    self.lbl_cdp.setText(f"🔎 已探测到 {name} 正在监听 CDP 端口 {ports[0]}，已回填 {extra}")
                else:
                    self.in_port.setText(str(self._next_port(9229)))
                    self.lbl_cdp.setText(f"⚠ {name} 当前未监听任何端口（可能未启动或未带调试参数），已自动分配新端口")

            def _pick(self, item):
                name = item.data(_Qt.UserRole)
                if not name:
                    return
                self.in_proc.setText(name)
                self._apply_proc(name)

            def initializePage(self, pid):
                if pid == 4:
                    is_web = not self.rb_local.isChecked()
                    self.lbl_proc.setText("浏览器：" if is_web else "进程名：")
                    self.btn_scan.setText("🔍 扫描浏览器进程" if is_web else "🔍 扫描当前进程（显示中文）")
                    self.in_proc.setPlaceholderText("如 msedge / chrome" if is_web else "如 CodeBuddy CN")
                    if is_web and not self.in_port.text():
                        self.in_port.setText(str(self._next_port(9222)))
                    # 进入本页自动扫描：列表直接按已输入的进程名过滤出最相近项
                    self._scan()

            def nextId(self):
                c = self.currentId()
                if c == 0:
                    return 1
                if c == 1:
                    return 2 if self.rb_local.isChecked() else 3
                if c in (2, 3):
                    return 4
                return -1

            def previousId(self):
                c = self.currentId()
                if c == 4:
                    return 2 if self.rb_local.isChecked() else 3
                if c in (2, 3):
                    return 1
                return super().previousId()

        w = Wizard(existing)
        if w.exec() != QWizard.Accepted:
            return None, False
        n = w.in_name.text().strip()
        if not n:
            self.log_line("⚠ 名字不能为空")
            return None, False
        is_local = w.rb_local.isChecked()
        proc = w.in_proc.text().strip()
        entry = {"名字": n, "类型": "electron" if is_local else "web",
                 "进程名": proc or n, "启用": True}
        if is_local:
            entry["exe"] = w.in_exe.text().strip()
        else:
            entry["url"] = w.in_url.text().strip()
            entry["浏览器"] = proc or "msedge"
        pt = w.in_port.text().strip()
        try:
            entry["cdp_port"] = int(pt) if pt else None
        except Exception:
            entry["cdp_port"] = None
        return entry, True

    def add_player(self):
        """点击「➕ 添加AI平台」入口。"""
        entry, ok = self._player_wizard()
        if not ok:
            return
        ps = load_players()
        ps.append(entry)
        save_players(ps)
        self.rebuild_table()
        self.log_line(f"✅ 已添加选手: {entry['名字']}")

    def edit_player(self, name):
        """右键「修改配置」入口：可重新配置名字、重扫进程/浏览器及 CDP 端口。"""
        ps = load_players()
        old = next((x for x in ps if x.get("名字") == name), None)
        if not old:
            self.log_line(f"⚠ 找不到选手: {name}")
            return
        entry, ok = self._player_wizard(old)
        if not ok:
            return
        for i, x in enumerate(ps):
            if x.get("名字") == name:
                ps[i] = entry
                break
        save_players(ps)
        self.rebuild_table()
        self.log_line(f"✅ 已更新选手: {entry['名字']}")

    def open_result_dir(self):
        try:
            paths.open_output_folder()
        except Exception as e:
            self.log_line("打开产出文件夹失败: " + str(e))

    def open_workspace_dir(self):
        try:
            paths.open_workspace_folder()
        except Exception as e:
            self.log_line("打开工作区失败: " + str(e))

    def on_stop(self):
        collab_exec.stop()
        self.log_line("⏹ 已请求停止（协同写作）")

    def restart_app(self):
        import subprocess
        self.log_line("🔄 正在重启…")
        exe = sys.executable
        argv = list(sys.argv)
        # 脚本路径解析成绝对路径，避免 cwd 变化导致重启失败
        if argv and not os.path.isabs(argv[0]):
            argv = [os.path.abspath(argv[0])] + argv[1:]
        try:
            # 普通子进程（继承当前会话 / 显示器），确保新窗口能正常弹出
            subprocess.Popen([exe] + argv, cwd=os.getcwd())
        except Exception as e:
            self.log_line(f"❌ 重启失败(Popen): {e}，尝试直接替换进程…")
            try:
                os.execv(exe, [exe] + argv)
            except Exception as e2:
                self.log_line(f"❌ 兜底重启也失败: {e2}")
                return
        # 退出当前进程，新进程独立存活
        sys.exit(0)

    def refresh_all(self):
        self.rebuild_table()
        self.refresh_status()
        if hasattr(self, "pipeline_panel"):
            try:
                self.pipeline_panel.refresh()
            except Exception:
                pass
        if hasattr(self, "monitor"):
            try:
                self.monitor.refresh()
            except Exception:
                pass

    # -------------------------------------------------------------- 单聊
    def quick_send(self):
        sys.path.insert(0, paths.WINDOWS_USE)
        try:
            from mix_send import send
        except Exception as e:
            self.log_line(f"❌ 无法加载 mix_send: {e}")
            return
        ai = self.chat_ai.currentText().strip()
        txt = self.chat_in.text().strip()
        if not ai or not txt:
            return
        try:
            r = send(ai, txt)
            self.log_line(f"📨 {ai} ← {r}")
        except Exception as e:
            self.log_line(f"❌ {ai} 发送失败: {e}")
        self.chat_in.clear()

    # -------------------------------------------------------------- 协同写作标签页（公共）
    def build_collab_tab(self):
        """构造「协同写作」标签页：环节编排 / AI 指派 + 放行·执行控制。"""
        w = QWidget()
        v = QVBoxLayout(w)

        tw = QTabWidget()
        self.stage_board = StageBoard()
        self.assign_panel = AssignPanel()
        tw.addTab(self.stage_board, "① 环节编排")
        tw.addTab(self.assign_panel, "② AI 指派")
        v.addWidget(tw)

        crow = QHBoxLayout()
        crow.addWidget(QLabel("当前大环节:"))
        self.c_combo = QComboBox()
        self._fill_c_combo()
        crow.addWidget(self.c_combo)
        self.b_crun = QPushButton("▶ 执行本环节")
        self.b_cauto = QPushButton("🚀 全自动串跑")
        self.b_cstop = QPushButton("⏹ 停止")
        crow.addWidget(self.b_crun)
        crow.addWidget(self.b_cauto)
        crow.addWidget(self.b_cstop)
        crow.addStretch(1)
        v.addLayout(crow)

        self.assign_panel.run_callback = lambda sk: self._run_collab_stage(sk)
        self.b_crun.clicked.connect(self._run_collab_stage_current)
        self.b_cauto.clicked.connect(self._run_collab_auto)
        self.b_cstop.clicked.connect(self.on_stop)
        return w

    def _fill_c_combo(self):
        try:
            self.c_combo.clear()
            for l in sb.load_links():
                self.c_combo.addItem(l["name"], l["key"])
        except Exception:
            pass

    def _run_collab_stage(self, sk):
        dry = self.cb_dry.isChecked()
        pr_set_dry_run(dry)
        collab_exec.set_dry_run(dry)
        self.log_line(f"=== 运行大环节: {sk} (dry={dry}) ===")
        try:
            collab_exec.run_stage(sk, self.log_line, dry)
            self.assign_panel.refresh()
        except Exception as e:
            self.log_line(f"err: {e}")

    def _run_collab_stage_current(self):
        sk = self.assign_panel.run_state["current_stage"]
        self._run_collab_stage(sk)

    def _run_collab_auto(self):
        dry = self.cb_dry.isChecked()
        pr_set_dry_run(dry)
        collab_exec.set_dry_run(dry)
        self.log_line("🚀 启动程序二全自动串跑")
        collab_exec.run_all_threaded(log_fn=self.log_line, dry=dry,
                                     done_fn=self._collab_auto_done)

    def _collab_auto_done(self):
        self.log_line("✅ 程序二全自动结束")


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    apply_dark(app)
    w = ConsoleBase("控制台底座（自测）")
    w.tab.addTab(w.build_collab_tab(), "协同写作")
    w.show()
    sys.exit(app.exec())
