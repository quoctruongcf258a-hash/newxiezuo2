"""在 F 盘副本里复刻 __main__ 启动流程，逐步打印，定位窗口为何不出现。"""
import sys, os, traceback, time

ROOT = r"F:\赛马23环整合工作室\程序2改装版"
APPDIR = os.path.join(ROOT, "app")
sys.path.insert(0, APPDIR)
os.chdir(ROOT)

def step(msg):
    print(f"[STEP] {msg}", flush=True)

try:
    from PySide6.QtWidgets import QApplication, QFileDialog
    step("PySide6 imported")
    app = QApplication(sys.argv)
    step("QApplication created")

    import paths
    step(f"paths.RULES_PATH={paths.RULES_PATH} exists={os.path.exists(paths.RULES_PATH)}")
    step(f"DEFAULT_OUTPUT={paths.DEFAULT_OUTPUT} writable={paths._is_writable(paths.DEFAULT_OUTPUT)}")

    asked = {"v": None}
    def ask(start):
        asked["v"] = start
        step(f"!! 弹框请求：选择产物根目录 start={start}（脚本内不弹，直接取消）")
        return ""
    paths.init_output_root(ask)
    step(f"init_output_root -> {paths.get_output_root()}  曾请求弹框={asked['v']}")

    import collab_app
    step("collab_app imported")
    w = collab_app.CollabApp()
    step("CollabApp() 构造完成")
    w.show()
    step(f"show() 完成 visible={w.isVisible()} title={w.windowTitle()!r}")

    def do_shot():
        try:
            import win32gui, win32ui, win32con, win32process
            from PIL import Image
            me = os.getpid()
            hits = []
            def cb(h, _):
                _, pid = win32process.GetWindowThreadProcessId(h)
                if pid == me and win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h):
                    hits.append((h, win32gui.GetWindowText(h)))
                return True
            win32gui.EnumWindows(cb, None)
            step(f"本进程可见窗口 {hits}")
            if hits:
                h, t = hits[0]
                try:
                    win32gui.SetForegroundWindow(h)
                except Exception:
                    pass
                time.sleep(1.0)
                l, tp, r, b = win32gui.GetWindowRect(h)
                w, hh = r - l, b - tp
                hdc = win32gui.GetWindowDC(h)
                udc = win32ui.CreateDCFromHandle(hdc)
                mem = udc.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(udc, w, hh)
                mem.SelectObject(bmp)
                mem.BitBlt((0, 0), (w, hh), udc, (0, 0), win32con.SRCCOPY)
                info = bmp.GetInfo()
                img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                                       bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1)
                out = r"F:\赛马23环整合工作室\_整合工作区\fgui_shot.png"
                img.save(out)
                step(f"已截图 {out} {img.size} title={t!r}")
                win32gui.ReleaseDC(h, hdc)
        except Exception:
            traceback.print_exc()
        app.quit()

    from PySide6.QtCore import QTimer
    QTimer.singleShot(9000, do_shot)
    app.exec()
    step("事件循环正常退出")
except Exception:
    traceback.print_exc()
    sys.exit(3)
