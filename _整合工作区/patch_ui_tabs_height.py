# patch_ui_tabs_height.py — 防止切 tab 后高度塌陷
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_tabs_height")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "self.tabs.setMinimumHeight(620)" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_tabsh")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 在 self.tabs.tabBar().hide() 之后插入 setMinimumHeight
    anchor = "self.tabs.tabBar().hide()"
    insert = ("self.tabs.tabBar().hide()\n"
              "        self.tabs.setMinimumHeight(620)")
    if anchor not in text:
        print("[失败] 锚点未找到：self.tabs.tabBar().hide()")
        return
    text = text.replace(anchor, insert, 1)
    print("✔ 已给 self.tabs 加 setMinimumHeight(620)")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()