"""当前轮次进度监控 + 单行补发"""
import os, sys, threading, time
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.WINDOWS_USE)
from PySide6.QtWidgets import (QProgressBar, QGroupBox, QTableWidget, QTableWidgetItem,
                                QHeaderView, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QComboBox)
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QColor

ROOT = os.path.join(os.path.expanduser("~"), "Desktop", "新书", "火影忍者", "七人赛马")
AIS = ["CodeBuddy", "QUEST", "Doubao", "Qianwen", "WorkBuddy", "ZCode"]

ROUNDS = [
    ("规划",       "产出/规划轮",     7, "规划轮",     "plain"),
    ("章纲",       "产出/章纲轮",     5, "章纲轮",     "plain"),
    ("正文-18A",   "产出/正文轮",     1, "正文轮",     "plain"),
    ("互审-规划",  "评审/规划轮",     5, "规划轮评审", "batch"),
    ("互审-章纲",  "评审/章纲轮",     5, "章纲轮评审", "batch"),
    ("互审-正文",  "评审/正文轮",     5, "正文轮评审", "batch"),
    ("终审-规划",  "评审/规划轮终审", 1, "规划轮终审", "plain"),
    ("终审-章纲",  "评审/章纲轮终审", 1, "章纲轮终审", "plain"),
]


class _Emitter(QObject):
    log = Signal(str)


class MonitorPanel(QGroupBox):
    def __init__(self, log_fn):
        super().__init__("④ 当前轮次进度")
        self.log_fn = log_fn
        self.emitter = _Emitter()
        self.emitter.log.connect(self.log_fn)
        self._busy = False

        v = QVBoxLayout(self)

        # 顶部：轮次选择
        top = QHBoxLayout()
        top.addWidget(QLabel("轮次:"))
        self.combo = QComboBox()
        for rn, *_ in ROUNDS:
            self.combo.addItem(rn)
        self.combo.setCurrentText("正文-18A")
        self.combo.currentIndexChanged.connect(self.refresh)
        top.addWidget(self.combo)

        self.b_refresh = QPushButton("🔄")
        self.b_refresh.setMaximumWidth(50)
        self.b_refresh.clicked.connect(self.refresh)
        top.addWidget(self.b_refresh)

        self.lbl_sum = QLabel("0/6")
        top.addWidget(self.lbl_sum)
        top.addStretch()
        v.addLayout(top)

        # 表格：AI | 状态 | 进度 | 操作
        self.table = QTableWidget(len(AIS), 3)
        self.table.setHorizontalHeaderLabels(["AI", "进度", "操作"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 110)
        self.table.setMaximumHeight(220)
        v.addWidget(self.table)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(3000)
        self.refresh()

    def cur_round(self):
        rn = self.combo.currentText()
        for r in ROUNDS:
            if r[0] == rn: return r
        return ROUNDS[0]

    def count_deliver(self, ai, subdir, need):
        d = os.path.join(ROOT, ai, subdir)
        if not os.path.isdir(d):
            return 0, need, False
        files = [f for f in os.listdir(d) if f.endswith((".md", ".json"))]
        return len(files), need, (len(files) >= need)

    def refresh(self):
        import datetime
        try:
            self._refresh_impl()
        except Exception as e:
            self.emitter.log.emit(f'refresh 出错: {e}')

    def _refresh_impl(self):
        _, subdir, need, _, _ = self.cur_round()
        done = 0
        for i, ai in enumerate(AIS):
            n, need_n, ok = self.count_deliver(ai, subdir, need)
            self.table.setItem(i, 0, QTableWidgetItem(ai))

            if ok: done += 1

            pct = int(min(n / need_n, 1.0) * 100) if need_n else 0
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(True)
            bar.setFormat(f"{pct}%")
            bar.setMaximumHeight(22)
            if ok:
                color = "#2e7d32"     # 绿
            elif pct > 0:
                color = "#ef6c00"     # 橙
            else:
                color = "#555"        # 灰
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #2d2d30;
                    border: 1px solid #3c3c3c;
                    border-radius: 3px;
                    text-align: center;
                    color: #d4d4d4;
                    font-size: 11px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
            self.table.setCellWidget(i, 1, bar)

            # 操作列：所有行都有补发按钮
            self.table.removeCellWidget(i, 2)
            if ok:
                btn = QPushButton("🔄 重发")
            else:
                btn = QPushButton("📤 补发")
            btn.setMaximumWidth(90)
            btn.clicked.connect(lambda _, idx=i: self.resend_one(idx))
            self.table.setCellWidget(i, 2, btn)

        self.lbl_sum.setText(f"{done}/6")

    # ---------- 单行补发 ----------
    def resend_one(self, idx):
        if self._busy:
            self.emitter.log.emit("⚠ 上次补发还在跑")
            return
        ai = AIS[idx]
        _, subdir, need, cmd_dir_name, mode = self.cur_round()

        cmd_dir = os.path.join(ROOT, "资料", "指令", cmd_dir_name)
        if not os.path.isdir(cmd_dir):
            self.emitter.log.emit(f"❌ 找不到指令目录: {cmd_dir}")
            return

        self._busy = True
        self.emitter.log.emit(f"📤 单发 {ai}")
        t = threading.Thread(target=self._do_resend_one, args=(ai, cmd_dir, mode), daemon=True)
        t.start()

    def _do_resend_one(self, ai, cmd_dir, mode):
        from mix_send import send
        try:
            if mode == "plain":
                fp = os.path.join(cmd_dir, f"{ai}.txt")
                if not os.path.exists(fp):
                    self.emitter.log.emit(f"❌ {ai}: 找不到 {fp}")
                    return
                text = open(fp, encoding="utf-8").read()
                self.emitter.log.emit(f"→ {ai} ({len(text.encode('utf-8'))//1024}KB)")
                r = send(ai, text)
                self.emitter.log.emit(f"  {r}")
            else:
                files = sorted([f for f in os.listdir(cmd_dir) if f.startswith(ai + "_") and f.endswith(".txt")])
                if not files:
                    self.emitter.log.emit(f"❌ {ai}: 无批次文件")
                    return
                for k, fn in enumerate(files, 1):
                    text = open(os.path.join(cmd_dir, fn), encoding="utf-8").read()
                    self.emitter.log.emit(f"→ {ai} 第{k}批 ({len(text.encode('utf-8'))//1024}KB)")
                    r = send(ai, text)
                    self.emitter.log.emit(f"  {r}")
                    time.sleep(3)
        except Exception as e:
            self.emitter.log.emit(f"❌ {ai}: {e}")
        finally:
            self._busy = False
