"""ui_main.py — 程序一 · 赛马全自动控制台（继承 ConsoleBase）。

布局：顶部工具栏 + 左侧选手停靠栏 + 中央标签页（流水线 / 监控 / 协同写作 / 脚本）
      + 底部日志·单聊栏。复用 ui_base.ConsoleBase 的公共结构，仅补充程序一独有功能。
"""
import os
import sys
import psutil

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QGroupBox, QTabWidget, QComboBox, QLineEdit, QWizard, QWizardPage,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QLabel)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor

from players import load_players, save_players
from scripts import list_scripts, run_async, SCRIPTS
from pipeline_panel import PipelinePanel
from monitor_panel import MonitorPanel
from ui_base import ConsoleBase, apply_dark


class MainWindow(ConsoleBase):
    def __init__(self):
        super().__init__("赛马全自动控制台 v0.8")
        self._proc = None
        self._timer = None

        self.tab.addTab(self._build_pipeline_tab(), "① 流水线")
        self.tab.addTab(self._build_monitor_tab(), "② 监控")
        self.tab.addTab(self.build_collab_tab(), "③ 协同写作")
        self.tab.addTab(self._build_script_tab(), "④ 脚本")

    # ----------------------------------------------------------- 标签页
    def _build_pipeline_tab(self):
        w = QWidget()
        v = QVBoxLayout(w)
        self.pipeline_panel = PipelinePanel(self.log_line)
        v.addWidget(self.pipeline_panel)
        row = QHBoxLayout()
        self.b_verify = QPushButton("✅ 验证完成")
        self.b_verify.setToolTip("检查当前阶段所有 AI 是否都已完成")
        self.b_verify.clicked.connect(self.pipeline_panel.verify_done)
        row.addWidget(self.b_verify)
        row.addStretch(1)
        v.addLayout(row)
        return w

    def _build_monitor_tab(self):
        w = QWidget()
        v = QVBoxLayout(w)
        self.monitor = MonitorPanel(self.log_line)
        v.addWidget(self.monitor)
        return w

    def _build_script_tab(self):
        w = QWidget()
        v = QVBoxLayout(w)
        g = QGroupBox("脚本运行器")
        gv = QGridLayout(g)
        gv.addWidget(QLabel("脚本:"), 0, 0)
        self.sbox = QComboBox()
        self.refresh_scripts()
        gv.addWidget(self.sbox, 0, 1, 1, 4)
        gv.addWidget(QLabel("参数:"), 0, 5)
        self.args = QLineEdit()
        self.args.setPlaceholderText("--batch 1 --only CodeBuddy")
        gv.addWidget(self.args, 0, 6, 1, 2)
        row2 = QHBoxLayout()
        self.b_run = QPushButton("▶ 运行")
        self.b_stop = QPushButton("⏹ 停止")
        self.b_ref = QPushButton("🔄 刷新脚本")
        self.b_open = QPushButton("📁 打开目录")
        for b in (self.b_run, self.b_stop, self.b_ref, self.b_open):
            row2.addWidget(b)
        gv.addLayout(row2, 1, 0, 1, 8)
        v.addWidget(g)
        v.addStretch(1)
        self.b_run.clicked.connect(self.run_selected)
        self.b_stop.clicked.connect(self.stop_script)
        self.b_ref.clicked.connect(self.refresh_scripts)
        self.b_open.clicked.connect(lambda: os.startfile(SCRIPTS))
        return w

    # ----------------------------------------------------------- 脚本运行
    def refresh_scripts(self):
        try:
            self.sbox.clear()
            self.sbox.addItems(list_scripts())
        except Exception:
            pass

    def run_selected(self):
        name = self.sbox.currentText()
        args = self.args.text().strip()
        self.log_line(f"▶ {name} {args}")
        if self._proc is not None and self._proc.poll() is None:
            self.log_line("⚠ 有脚本在跑，先停")
            return
        self._proc = run_async(name, args, None, None)
        if self._timer is None:
            self._timer = QTimer()
            self._timer.timeout.connect(self._read)
        self._timer.start(200)

    def _read(self):
        if self._proc is None:
            if self._timer:
                self._timer.stop()
            return
        try:
            while True:
                l = self._proc.stdout.readline()
                if not l:
                    break
                self.log.append(l.rstrip())
        except Exception:
            pass
        if self._proc.poll() is not None:
            self.log_line(f"✅ 结束 (code {self._proc.returncode})")
            self._proc = None
            if self._timer:
                self._timer.stop()

    def stop_script(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            self.log_line("⏹ 已终止")
        self._proc = None

    # ----------------------------------------------------------- 覆盖钩子
    def on_stop(self):
        import collab_exec
        collab_exec.stop()
        self.stop_script()
        self.log_line("⏹ 已请求停止（全部）")

    def open_result_dir(self):
        d = os.path.join(os.path.expanduser("~"), "Desktop", "新书", "火影忍者", "七人赛马", "_最终结果")
        try:
            os.makedirs(d, exist_ok=True)
            os.startfile(d)
        except Exception as e:
            self.log_line("打开目录失败: " + str(e))

    # add_player 已统一在 ConsoleBase 实现（5 步向导），此处直接继承即可。


if __name__ == "__main__":
    import sys as _sys
    from PySide6.QtWidgets import QApplication
    _app = QApplication(_sys.argv)
    apply_dark(_app)
    _win = MainWindow()
    _win.show()
    _sys.exit(_app.exec())
