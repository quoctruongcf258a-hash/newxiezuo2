# patch_ui_tabs_dyn.py — 按窗口高度动态设置 tabs 高度
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_tabs_dyn")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_dyn_tabs_h" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_tabsdyn")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 替换上一轮插入的固定 900 逻辑
    old = ("    def _update_nav(self):\n"
           "        # 防止切 tab 后高度塌陷：把 tabs 和里面每个 tab 都锁到同一高度\n"
           "        _tabs_min_h = 900\n"
           "        self.tabs.setMinimumHeight(_tabs_min_h)\n"
           "        for _i in range(self.tabs.count()):\n"
           "            _w = self.tabs.widget(_i)\n"
           "            if _w:\n"
           "                _w.setMinimumHeight(_tabs_min_h)\n")
    new = ("    def _update_nav(self):\n"
           "        # 动态按窗口高度设置 tabs 与每个 tab 的最小高度，防止切 tab 塌陷\n"
           "        if hasattr(self, 'tabs'):\n"
           "            _dyn_tabs_h = max(600, self.height() - 260)\n"
           "            self.tabs.setMinimumHeight(_dyn_tabs_h)\n"
           "            for _i in range(self.tabs.count()):\n"
           "                _w = self.tabs.widget(_i)\n"
           "                if _w:\n"
           "                    _w.setMinimumHeight(_dyn_tabs_h)\n"
           "            self.tabs.updateGeometry()\n")

    if old in text:
        text = text.replace(old, new, 1)
        print("✔ 已替换 _update_nav 里的固定 900 为动态高度")
    else:
        # 如果上一轮没跑成功，直接在函数头插入
        anchor = "    def _update_nav(self):\n"
        if anchor not in text:
            print("[失败] 找不到 _update_nav 函数")
            return
        text = text.replace(anchor, new, 1)
        print("✔ 已在 _update_nav 插入动态高度逻辑")

    # 同步改 resizeEvent
    old2 = ("    def resizeEvent(self, event):\n"
            "        if hasattr(self, 'tabs'):\n"
            "            for _i in range(self.tabs.count()):\n"
            "                _w = self.tabs.widget(_i)\n"
            "                if _w:\n"
            "                    _w.setMinimumHeight(900)\n"
            "            self.tabs.setMinimumHeight(900)\n")
    new2 = ("    def resizeEvent(self, event):\n"
            "        if hasattr(self, 'tabs'):\n"
            "            _dyn_tabs_h = max(600, self.height() - 260)\n"
            "            self.tabs.setMinimumHeight(_dyn_tabs_h)\n"
            "            for _i in range(self.tabs.count()):\n"
            "                _w = self.tabs.widget(_i)\n"
            "                if _w:\n"
            "                    _w.setMinimumHeight(_dyn_tabs_h)\n")
    if old2 in text:
        text = text.replace(old2, new2, 1)
        print("✔ 已更新 resizeEvent 的动态高度")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()