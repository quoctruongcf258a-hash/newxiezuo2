"""流水线控制 + 状态监控（最简版）"""
import os, sys, threading, time
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.WINDOWS_USE)
from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QColor
from pipeline import STAGES, KEY2STAGE, get_current_key, set_current_key, find_stage_index, check_stage, AIS, ROOT
from pipeline_runner import execute_stage, rerun_stage, _batch_targets, _done_targets, _batch_done, _md_names
from auto_pipeline import AutoPipeline

class _Emitter(QObject):
    log = Signal(str)
    done = Signal()

class PipelinePanel(QGroupBox):
    def __init__(self, log_fn):
        super().__init__("流水线控制")
        self.log_fn = log_fn
        self._busy = False
        self.emitter = _Emitter()
        self.emitter.log.connect(self.log_fn)
        self.emitter.done.connect(self._on_done)
        self._last_size = {}
        self._last_change = {}
        v = QVBoxLayout(self)
        l1 = QHBoxLayout()
        l1.addWidget(QLabel("阶段:"))
        self.combo = QComboBox()
        for s in STAGES:
            self.combo.addItem(s["name"], s["key"])
        l1.addWidget(self.combo)
        l1.addStretch()
        v.addLayout(l1)
        l2 = QHBoxLayout()
        self.lbl_state = QLabel("")
        l2.addWidget(self.lbl_state)
        self.b_prev = QPushButton("回退"); self.b_prev.setMaximumWidth(70)
        self.b_refresh = QPushButton("刷新"); self.b_refresh.setMaximumWidth(70)
        self.b_run = QPushButton("执行"); self.b_run.setMaximumWidth(80)
        self.b_rerun = QPushButton("🔄 重跑本阶段"); self.b_rerun.setMaximumWidth(110)
        self.b_next = QPushButton("推进"); self.b_next.setMaximumWidth(70)
        self.b_auto = QPushButton("🚀 全自动")
        self.b_auto.setToolTip("从当前阶段一路跑到最后")
        self.b_stop = QPushButton("⏹ 停止")
        self.b_stop.setEnabled(False)
        for b in [self.b_prev, self.b_refresh, self.b_run, self.b_rerun, self.b_next]:
            l2.addWidget(b)
        l2.addStretch()
        l2.setSpacing(12)
        v.addLayout(l2)
        self.table = QTableWidget(len(AIS), 3)
        self.table.setHorizontalHeaderLabels(["AI", "状态", "操作"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(2, 100)
        self.table.setMaximumHeight(220)
        v.addWidget(self.table)
        self.b_prev.clicked.connect(self.go_prev)
        self.b_refresh.clicked.connect(self.refresh)
        self.b_run.clicked.connect(self.run_step)
        self.b_rerun.clicked.connect(self.rerun_step)
        self.b_next.clicked.connect(self.go_next)
        self.b_auto.clicked.connect(self.start_auto)
        self.b_stop.clicked.connect(self.stop_auto)
        self.combo.currentIndexChanged.connect(self._on_pick)
        cur = get_current_key()
        self.combo.setCurrentIndex(find_stage_index(cur))
        self.timer = QTimer(); self.timer.timeout.connect(self.refresh); self.timer.start(5000)
        self.ftimer = QTimer(); self.ftimer.timeout.connect(self.refresh_status); self.ftimer.start(1500)
        self.refresh()
        self.refresh_status()

    def verify_done(self):
        import os as _os
        s = self._stage()
        if not s:
            self.emitter.log.emit("无法验证：未选中阶段")
            return
        self.emitter.log.emit("─── 验证阶段: " + s["name"] + " ───")
        self.emitter.log.emit("   扫盘中，请稍候...")
        ok_n, total_n, all_done = check_stage(s)
        check = s["check"]
        need = s.get("need", 1)
        done_list = []
        miss_list = []
        if check.startswith("_融合产物"):
            d = _os.path.join(ROOT, check)
            n = 0
            if _os.path.isdir(d):
                n = len([f for f in _os.listdir(d) if f.endswith(".md")])
            if n >= 1:
                done_list.append("融合产物(" + str(n) + "/1)")
            else:
                miss_list.append("融合产物(0/1)")
        else:
            for ai in AIS:
                d = _os.path.join(ROOT, ai, check)
                n = 0
                if _os.path.isdir(d):
                    n = len([f for f in _os.listdir(d) if f.endswith((".md", ".json"))])
                if n >= need:
                    done_list.append(ai + "(" + str(n) + "/" + str(need) + ")")
                else:
                    miss_list.append(ai + "(" + str(n) + "/" + str(need) + ")")
        self.emitter.log.emit("   官方判定: " + str(ok_n) + "/" + str(total_n) + (" 全齐" if all_done else " 未全齐"))
        self.emitter.log.emit("   逐家扫盘：")
        if done_list:
            self.emitter.log.emit("    ✅ 已完成: " + "、".join(done_list))
        if miss_list:
            self.emitter.log.emit("    ❌ 未完成: " + "、".join(miss_list))
        if all_done and not miss_list:
            self.emitter.log.emit("✅ 验证通过：" + str(ok_n) + "/" + str(total_n) + "，可以推进到下一阶段")
        else:
            self.emitter.log.emit("⚠ 验证未通过：" + str(ok_n) + "/" + str(total_n) + "，请重发缺失家")
        return all_done

    def _on_pick(self):
        set_current_key(self.combo.currentData())
        self._last_size.clear(); self._last_change.clear()
        self.refresh(); self.refresh_status()

    def _stage(self):
        return KEY2STAGE.get(self.combo.currentData())

    def _stats(self, ai, check, prefix='', need=1):
        if check.startswith('_融合产物'):
            d = os.path.join(ROOT, check)
        else:
            d = os.path.join(ROOT, ai, check)
        if not os.path.isdir(d): return 0, 0
        total = 0
        qualified = 0
        for f in os.listdir(d):
            if not f.endswith(('.md', '.json')): continue
            if prefix and not f.startswith(prefix): continue
            fp2 = os.path.join(d, f)
            try:
                sz = os.path.getsize(fp2)
                total += sz
                if sz >= 500:
                    qualified += 1
            except: pass
        return qualified, total
    def refresh(self):
        s = self._stage()
        if not s: return
        self.setTitle("流水线控制 - " + s["name"])
        ok, total, done = check_stage(s)
        pct = int(ok / total * 100) if total else 0
        color = "#4ec9b0" if done else ("orange" if ok > 0 else "#d4d4d4")
        self.lbl_state.setText(str(ok) + "/" + str(total) + " (" + str(pct) + "%)")
        self.lbl_state.setStyleSheet("color: " + color + "; font-weight: bold;")

    def refresh_status(self):
        s = self._stage()
        if not s: return
        check = s["check"]
        now = time.time()
        need = s.get("need", 1)
        prefix = s.get("prefix", "")
        for i, ai in enumerate(AIS):
            self.table.setItem(i, 0, QTableWidgetItem(ai))
            qualified, size = self._stats(ai, check, prefix, need)
            # 用"达标数+总大小"作变化指纹
            fp = (qualified, size)
            prev = self._last_size.get(ai, (-1, -1))
            if fp != prev:
                self._last_size[ai] = fp
                self._last_change[ai] = now
            last_change = self._last_change.get(ai, now)
            age = now - last_change
            it = QTableWidgetItem()
            if qualified == 0:
                it.setText("未开始")
                it.setForeground(QColor("gray"))
            elif qualified < need:
                # 部分达标
                if age < 3:
                    it.setText("生成中 (" + str(qualified) + "/" + str(need) + "，{:.1f}KB)".format(size/1024))
                    it.setForeground(QColor("#4ec9b0"))
                else:
                    it.setText("部分 (" + str(qualified) + "/" + str(need) + "，{:.1f}KB)".format(size/1024))
                    it.setForeground(QColor("orange"))
            else:
                # 全达标
                if age < 3:
                    it.setText("生成中 (" + str(qualified) + "/" + str(need) + "，{:.1f}KB)".format(size/1024))
                    it.setForeground(QColor("#4ec9b0"))
                else:
                    it.setText("已完成 (" + str(qualified) + "/" + str(need) + "，{:.1f}KB)".format(size/1024))
                    it.setForeground(QColor("green"))
            self.table.setItem(i, 1, it)
            self.table.removeCellWidget(i, 2)
            btn = QPushButton("重发")
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda _, idx=i: self.resend_one(idx))
            self.table.setCellWidget(i, 2, btn)

    def resend_one(self, idx):
        ai = AIS[idx]
        s = self._stage()
        cmd_dir = os.path.join(ROOT, "资料", "指令", s["cmd_dir"])
        if not os.path.isdir(cmd_dir):
            self.emitter.log.emit("找不到目录: " + cmd_dir)
            return
        def run():
            from mix_send import send
            try:
                action = s["action"]
                if action in ("broadcast", "broadcast_one"):
                    fp = os.path.join(cmd_dir, ai + ".txt")
                    if not os.path.exists(fp):
                        fp = os.path.join(cmd_dir, "公共.txt")
                    if not os.path.exists(fp):
                        files = [f for f in os.listdir(cmd_dir) if f.endswith(".txt")]
                        if files: fp = os.path.join(cmd_dir, files[0])
                    if not os.path.exists(fp):
                        self.emitter.log.emit("无指令: " + ai); return
                    text = open(fp, encoding="utf-8").read()
                    self.emitter.log.emit("重发 -> " + ai)
                    r = send(ai, text)
                    self.emitter.log.emit("  " + r)
                elif action == "broadcast_batch":
                    files = sorted([f for f in os.listdir(cmd_dir) if f.startswith(ai + "_") and f.endswith(".txt")])
                    if not files:
                        self.emitter.log.emit("无批次: " + ai); return
                    WINDOW_SEC = 30 * 60
                    POLL_SEC = 15
                    send_cnt = 0
                    for k, fn in enumerate(files, 1):
                        fp = os.path.join(cmd_dir, fn)
                        targets = _batch_targets(fp)
                        if _batch_done(ai, s["check"], k, targets):
                            self.emitter.log.emit("  " + ai + " 第" + str(k) + "批 已齐，跳过")
                            continue
                        text = open(fp, encoding="utf-8").read()
                        desc = ("目标 " + "/".join(targets)) if targets else "无解析目标"
                        while True:
                            self.emitter.log.emit("重发 -> " + ai + " 第" + str(k) + "批 (" + desc + ")")
                            r = send(ai, text)
                            self.emitter.log.emit("  " + r)
                            send_cnt += 1
                            t0 = time.time()
                            finish = False
                            while time.time() - t0 < WINDOW_SEC:
                                time.sleep(POLL_SEC)
                                if _batch_done(ai, s["check"], k, targets):
                                    self.emitter.log.emit("  ✅ " + ai + " 第" + str(k) + "批 已落盘 (耗时 " + str(int(time.time()-t0)) + "s)")
                                    finish = True
                                    break
                            if finish:
                                break
                            self.emitter.log.emit("  ⚠ " + ai + " 第" + str(k) + "批 超 30 分钟未齐，重发本批")
                    if send_cnt == 0:
                        self.emitter.log.emit("  " + ai + " 全部批次已齐，无需重发")
                elif action == "merge":
                    if ai != "ZCode":
                        self.emitter.log.emit("融合只发 ZCode"); return
                    files = sorted([f for f in os.listdir(cmd_dir) if f.endswith(".txt")])
                    WINDOW_SEC = 30 * 60
                    POLL_SEC = 15
                    target_dir = os.path.join(ROOT, s["check"])
                    for k, fn in enumerate(files, 1):
                        text = open(os.path.join(cmd_dir, fn), encoding="utf-8").read()
                        while True:
                            before = _md_names(target_dir)
                            self.emitter.log.emit("重发 -> ZCode 第" + str(k) + "批")
                            r = send(ai, text)
                            self.emitter.log.emit("  " + r)
                            t0 = time.time()
                            finish = False
                            while time.time() - t0 < WINDOW_SEC:
                                time.sleep(POLL_SEC)
                                if _md_names(target_dir) - before:
                                    self.emitter.log.emit("  ✅ 第" + str(k) + "批 已落盘 (耗时 " + str(int(time.time()-t0)) + "s)")
                                    finish = True
                                    break
                            if finish:
                                break
                            self.emitter.log.emit("  ⚠ 第" + str(k) + "批 超 30 分钟未落盘，重发本批")
            except Exception as e:
                self.emitter.log.emit("err: " + str(e))
        threading.Thread(target=run, daemon=True).start()

    def run_step(self):
        if self._busy:
            self.emitter.log.emit("上一步还在跑"); return
        key = self.combo.currentData()
        s = KEY2STAGE.get(key)
        self.emitter.log.emit("=== 执行: " + s["name"] + " ===")
        self._busy = True
        self.b_run.setEnabled(False)
        threading.Thread(target=self._do_run, args=(key,), daemon=True).start()

    def _do_run(self, key):
        try:
            ok, total = execute_stage(key, lambda m: self.emitter.log.emit(m))
            self.emitter.log.emit("完成: " + str(ok) + "/" + str(total))
        except Exception as e:
            self.emitter.log.emit("err: " + str(e))
        finally:
            self._busy = False
            self.emitter.done.emit()

    def _on_done(self):
        self.b_run.setEnabled(True)
        self.refresh()

    def rerun_step(self):
        if self._busy:
            self.emitter.log.emit("上一步还在跑"); return
        key = self.combo.currentData()
        s = KEY2STAGE.get(key)
        if not s:
            self.emitter.log.emit("无法重跑：未选中阶段"); return
        self.emitter.log.emit("=== 重跑: " + s["name"] + " ===")
        self._busy = True
        self.b_rerun.setEnabled(False)
        threading.Thread(target=self._do_rerun, args=(key,), daemon=True).start()

    def _do_rerun(self, key):
        try:
            ok, total = rerun_stage(key, lambda m: self.emitter.log.emit(m))
            self.emitter.log.emit("完成: " + str(ok) + "/" + str(total))
        except Exception as e:
            self.emitter.log.emit("err: " + str(e))
        finally:
            self._busy = False
            self.b_rerun.setEnabled(True)
            self.emitter.done.emit()

    def go_next(self):
        idx = find_stage_index(self.combo.currentData())
        if idx + 1 >= len(STAGES):
            self.emitter.log.emit("已是最后一步"); return
        set_current_key(STAGES[idx + 1]["key"])
        self.combo.setCurrentIndex(idx + 1)

    def go_prev(self):
        idx = find_stage_index(self.combo.currentData())
        if idx == 0:
            self.emitter.log.emit("已是第一步"); return
        set_current_key(STAGES[idx - 1]["key"])
        self.combo.setCurrentIndex(idx - 1)

    def start_auto(self):
        if self._busy:
            self.emitter.log.emit("⚠ 已有任务在跑")
            return
        self._busy = True
        self.b_auto.setEnabled(False)
        self.b_stop.setEnabled(True)
        self.emitter.log.emit("🚀 启动全自动流水线")
        self._auto = AutoPipeline(
            log_fn=lambda m: self.emitter.log.emit(m),
            done_fn=self._auto_done,
        )
        self._auto.start()

    def stop_auto(self):
        if hasattr(self, "_auto") and self._auto:
            self._auto.stop()
        self.emitter.log.emit("⏹ 已请求停止")

    def _auto_done(self):
        self._busy = False
        self.b_auto.setEnabled(True)
        self.b_stop.setEnabled(False)
        self.emitter.log.emit("✅ 全自动结束")
