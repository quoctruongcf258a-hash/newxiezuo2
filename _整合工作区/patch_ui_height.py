# patch_ui_height.py — 修复 33 行放不下的问题
# 1) top 高度改成弹性，日志区压缩
# 2) tabs 里的面板套 QScrollArea，内容超长可滚
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")

CHANGES = [
    # 1. top 不再固定高度
    ("        self.top.setFixedHeight(545)",
     "        self.top.setMinimumHeight(500)"),
    # 2. top 占大头，日志区压缩
    ("        cv.addWidget(self.top)\n"
     "        cv.addWidget(force_row)\n"
     "        cv.addWidget(self.log_chat, 1)",
     "        cv.addWidget(self.top, 1)\n"
     "        cv.addWidget(force_row)\n"
     "        self.log_chat.setMaximumHeight(240)\n"
     "        cv.addWidget(self.log_chat)"),
    # 3. 面板外面套滚动
    ("            cv.addWidget(panel, 1, _Qt.AlignTop)\n            cv.addStretch(1)",
     "            scroll = QScrollArea()\n"
     "            scroll.setWidgetResizable(True)\n"
     "            scroll.setHorizontalScrollBarPolicy(_Qt.ScrollBarAlwaysOff)\n"
     "            scroll.setStyleSheet(\"QScrollArea{border:none;}\")\n"
     "            scroll.setWidget(panel)\n"
     "            cv.addWidget(scroll, 1)"),
]


def main():
    print("=" * 60)
    print("patch_ui_height — 修复高度布局")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "scroll = QScrollArea()" in text and "self.log_chat.setMaximumHeight(240)" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_height")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    ok = 0
    for i, (a, b) in enumerate(CHANGES, 1):
        if a not in text:
            print(f"[失败] 改动{i} 锚点未找到")
            print(f"      前 80 字：{a[:80]!r}")
            continue
        text = text.replace(a, b, 1)
        print(f"✔ 改动{i}")
        ok += 1

    if ok == 0:
        print("\n[中止] 没有一处改动成功")
        return

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}（成功 {ok}/{len(CHANGES)} 处）")


if __name__ == "__main__":
    main()