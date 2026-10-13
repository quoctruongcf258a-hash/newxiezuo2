# patch_merge_green.py — 汇总者下拉也只列绿灯 AI
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_merge_green")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_merge_green_fix" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_mergegreen")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    old = '''    def _refresh_merge_combo(self):
        """刷新汇总者下拉（从 ai_apps.json 拿启用的 AI）。"""
        try:
            from players import load_players
            apps = load_players() or []
        except Exception:
            apps = []
        names = [x.get("名字", "") for x in apps if x.get("启用") is not False and x.get("名字")]
        cur = self.merge_combo.currentText() if hasattr(self, "merge_combo") else ""
        self.merge_combo.blockSignals(True)
        self.merge_combo.clear()
        self.merge_combo.addItems(names)
        if cur and cur in names:
            self.merge_combo.setCurrentText(cur)
        elif names:
            self.merge_combo.setCurrentIndex(0)
        self.merge_combo.blockSignals(False)
'''

    new = '''    def _refresh_merge_combo(self):
        """_merge_green_fix：汇总者下拉只列 CDP 通（绿灯）的 AI。"""
        try:
            from players import load_players
            apps = load_players() or []
        except Exception:
            apps = []

        def _alive(port):
            if not port:
                return False
            import socket
            for family, host in ((socket.AF_INET, "127.0.0.1"),
                                  (socket.AF_INET6, "::1")):
                try:
                    s = socket.socket(family, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect((host, port))
                    s.close()
                    return True
                except Exception:
                    continue
            return False

        names = [x.get("名字", "") for x in apps
                 if x.get("名字") and _alive(x.get("cdp_port"))]
        cur = self.merge_combo.currentText() if hasattr(self, "merge_combo") else ""
        self.merge_combo.blockSignals(True)
        self.merge_combo.clear()
        self.merge_combo.addItems(names)
        if cur and cur in names:
            self.merge_combo.setCurrentText(cur)
        elif names:
            self.merge_combo.setCurrentIndex(0)
        self.merge_combo.blockSignals(False)
'''

    if old not in text:
        print("[失败] 锚点未找到")
        return
    text = text.replace(old, new, 1)
    print("✔ 汇总者下拉改为只列绿灯 AI")

    # 加一个"刷新状态"时同步刷新汇总者的钩子
    # 找到 _sync_ais_to_players 末尾追加调用
    old2 = "        for p in getattr(self, \"stage_panels\", []):\n            p.set_ais(names)\n"
    new2 = old2 + "        # _merge_green_fix：状态刷新时同步刷新汇总者下拉\n        if hasattr(self, \"merge_combo\"):\n            self._refresh_merge_combo()\n"
    if old2 in text:
        text = text.replace(old2, new2, 1)
        print("✔ 刷新状态时同步刷新汇总者下拉")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()