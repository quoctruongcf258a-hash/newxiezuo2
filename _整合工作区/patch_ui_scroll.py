# patch_ui_scroll.py — 给 tabs 里的 scroll 加最小高度 + size policy
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_scroll")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "scroll.setMinimumHeight(700)" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_scroll")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    anchor = "            scroll.setWidget(panel)\n"
    insert = ("            scroll.setWidget(panel)\n"
              "            scroll.setMinimumHeight(700)\n"
              "            scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n")
    if anchor not in text:
        print("[失败] 锚点未找到：scroll.setWidget(panel)")
        return
    text = text.replace(anchor, insert, 1)
    print("✔ 已给 scroll 加 setMinimumHeight(700) + Expanding")

    # 同时给 container 也加
    anchor2 = "            cv.addWidget(scroll, 1)\n"
    insert2 = ("            container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n"
               "            cv.addWidget(scroll, 1)\n")
    if anchor2 in text:
        text = text.replace(anchor2, insert2, 1)
        print("✔ 已给 container 加 Expanding")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()