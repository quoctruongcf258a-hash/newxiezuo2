# patch_ui_tabs_height_v2.py
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_tabs_height_v2")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "self.tabs.setMinimumHeight(720)" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_tabsh2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    anchor = "        self.tabs = QTabWidget()\n"
    insert = ("        self.tabs = QTabWidget()\n"
              "        self.tabs.setMinimumHeight(720)\n")
    if anchor not in text:
        print("[失败] 锚点未找到：self.tabs = QTabWidget()")
        return
    text = text.replace(anchor, insert, 1)
    print("✔ 已给 self.tabs 加 setMinimumHeight(720)")

    # 同时给 work_split 加最小高度，防止 splitter 收缩
    anchor2 = "        self.work_split.addWidget(self.tabs)"
    insert2 = ("        self.work_split.setMinimumHeight(720)\n"
               "        self.work_split.addWidget(self.tabs)")
    if anchor2 in text:
        text = text.replace(anchor2, insert2, 1)
        print("✔ 已给 self.work_split 加 setMinimumHeight(720)")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()