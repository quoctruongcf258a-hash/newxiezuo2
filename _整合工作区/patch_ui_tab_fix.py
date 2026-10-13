# patch_ui_tab_fix.py — 切 tab 时强制 tabs 高度对齐
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_tab_fix")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_tabs_min_h" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_tabfix")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 1. 在 _update_nav 开头插入高度同步
    anchor = "    def _update_nav(self):\n"
    insert = ("    def _update_nav(self):\n"
              "        # 防止切 tab 后高度塌陷：把 tabs 和里面每个 tab 都锁到同一高度\n"
              "        _tabs_min_h = 900\n"
              "        self.tabs.setMinimumHeight(_tabs_min_h)\n"
              "        for _i in range(self.tabs.count()):\n"
              "            _w = self.tabs.widget(_i)\n"
              "            if _w:\n"
              "                _w.setMinimumHeight(_tabs_min_h)\n")
    if anchor not in text:
        print("[失败] 锚点未找到：def _update_nav(self):")
        return
    text = text.replace(anchor, insert, 1)
    print("✔ 已在 _update_nav 加高度同步")

    # 2. 在 resizeEvent 里也同步
    anchor2 = "    def resizeEvent(self, event):\n"
    insert2 = ("    def resizeEvent(self, event):\n"
               "        if hasattr(self, 'tabs'):\n"
               "            for _i in range(self.tabs.count()):\n"
               "                _w = self.tabs.widget(_i)\n"
               "                if _w:\n"
               "                    _w.setMinimumHeight(900)\n"
               "            self.tabs.setMinimumHeight(900)\n")
    if anchor2 in text:
        text = text.replace(anchor2, insert2, 1)
        print("✔ 已在 resizeEvent 加高度同步")
    else:
        print("[警告] resizeEvent 未找到（不影响，_update_nav 已覆盖）")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()