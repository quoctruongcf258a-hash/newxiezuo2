# patch_merge_no_check.py — 启动时下拉不检测 CDP
import shutil
import re
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_merge_no_check")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_no_check_mode" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_nochk")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 定位 _refresh_merge_combo 整个函数
    start_marker = "    def _refresh_merge_combo(self):"
    end_marker = "    def _export_roster_to_cli(self):"

    i = text.find(start_marker)
    j = text.find(end_marker)
    if i < 0 or j < 0 or j <= i:
        print(f"[失败] 找不到函数边界。start={i}, end={j}")
        return

    new_func = '''    def _refresh_merge_combo(self):
        """_no_check_mode：启动时不检测 CDP，直接列启用中的 AI（<0.1s）。"""
        try:
            from players import load_players
            apps = load_players() or []
        except Exception:
            apps = []
        names = [x.get("名字", "") for x in apps
                 if x.get("名字") and x.get("启用") is not False]
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
    print("✔ 已替换 _refresh_merge_combo 为不检测版")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()