# patch_ui_container_h.py — 每个 tab 的 container 统一最小高度
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_container_h")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "container.setMinimumHeight(900)" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_ch")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    anchor = "            container = QWidget()\n"
    insert = ("            container = QWidget()\n"
              "            container.setMinimumHeight(900)\n"
              "            container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n")
    if anchor not in text:
        print("[失败] 锚点未找到：container = QWidget()")
        return
    text = text.replace(anchor, insert, 1)
    print("✔ 已给 container 加 setMinimumHeight(900) + Expanding")

    # tabs 自身的 size policy 也设一下
    anchor2 = "        self.tabs.setMinimumHeight(720)\n"
    if anchor2 in text:
        text = text.replace(
            anchor2,
            "        self.tabs.setMinimumHeight(720)\n"
            "        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n",
            1)
        print("✔ 已给 self.tabs 加 Expanding 策略")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()