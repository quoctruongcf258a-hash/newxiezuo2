# patch_ui_top_h.py — 把 self.top 的高度限制解除
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_top_h")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_TOP_FIX" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_toph")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 1. self.top.setMinimumHeight(500) → 解除，改 Expanding
    old1 = "        self.top.setMinimumHeight(500)\n"
    new1 = ("        self.top.setMinimumHeight(500)  # _TOP_FIX\n"
            "        self.top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n"
            "        self.top.setMaximumHeight(16777215)\n")
    if old1 in text:
        text = text.replace(old1, new1, 1)
        print("✔ 已给 self.top 加 Expanding + 解除 maxHeight")
    else:
        # 可能之前是 setFixedHeight
        old1b = "        self.top.setFixedHeight(545)\n"
        if old1b in text:
            text = text.replace(old1b, new1, 1)
            print("✔ 已把 self.top 的 setFixedHeight(545) 改为 Expanding")
        else:
            print("[失败] 找不到 self.top 的高度设置")

    # 2. cv.addWidget(self.top, 1) 已经是 1，确认
    if "cv.addWidget(self.top, 1)" not in text:
        old2 = "cv.addWidget(self.top)\n"
        if old2 in text:
            text = text.replace(old2, "cv.addWidget(self.top, 1)\n", 1)
            print("✔ 已把 self.top 的 stretch 改为 1")

    # 3. log_chat 保持最大 240，但去掉 minHeight，让它不占主位
    if "self.log_chat.setMaximumHeight(240)" not in text:
        old3 = "cv.addWidget(self.log_chat, 1)\n"
        if old3 in text:
            text = text.replace(
                old3,
                "self.log_chat.setMaximumHeight(240)\ncv.addWidget(self.log_chat)\n", 1)
            print("✔ 已限制 self.log_chat 高度")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()