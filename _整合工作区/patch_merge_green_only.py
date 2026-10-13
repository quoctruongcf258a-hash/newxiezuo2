# patch_merge_green_only.py — 下拉只列绿灯（并发快检）
import shutil
import re
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_merge_green_only")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_green_only_mode" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_greenonly")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    start_marker = "    def _refresh_merge_combo(self):"
    i = text.find(start_marker)
    if i < 0:
        print("[失败] 找不到 _refresh_merge_combo")
        return

    rest = text[i + len(start_marker):]
    m = re.search(r"\n    def \w+\(self", rest)
    if not m:
        print("[失败] 找不到下一个 def")
        return
    j = i + len(start_marker) + m.start() + 1

    new_func = '''    def _refresh_merge_combo(self):
        """_green_only_mode：只列 CDP 通的 AI（并发 + 0.1s 超时，<1s 完成）。"""
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
                    s.settimeout(0.1)
                    s.connect((host, port))
                    s.close()
                    return True
                except Exception:
                    continue
            return False

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=24) as _ex:
            _res = list(_ex.map(lambda x: _alive(x.get("cdp_port")), apps))
        names = [x.get("名字", "") for x, ok in zip(apps, _res)
                 if x.get("名字") and ok]

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
    text = text[:i] + new_func + text[j:]
    print("✔ 已替换 _refresh_merge_combo 为并发绿灯检测版")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()