# patch_ui_columns.py — 让 AssignPanel 内的子环排成多列
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\assign_panel.py")

CHANGES = [
    # 1. __init__ 加 step_columns 参数
    ("def __init__(self, with_runner=True, stages=None, columns=1):",
     "def __init__(self, with_runner=True, stages=None, columns=1, step_columns=2):"),
    # 2. 保存参数
    ("        self.with_runner = with_runner\n        self.columns = max(1, int(columns))",
     "        self.with_runner = with_runner\n        self.columns = max(1, int(columns))\n"
     "        self.step_columns = max(1, int(step_columns))"),
    # 3. gv 从 QVBoxLayout 改 QGridLayout
    ("            gv = QVBoxLayout(g)\n            gv.setContentsMargins(6, 4, 6, 4)\n            gv.setSpacing(3)",
     "            gv = QGridLayout(g)\n            gv.setContentsMargins(6, 4, 6, 4)\n"
     "            gv.setSpacing(3)\n            gv.setHorizontalSpacing(10)"),
    # 4. head 横跨全部列
    ("            gv.addLayout(head)\n            self.badges[sk] = badge",
     "            gv.addLayout(head, 0, 0, 1, self.step_columns)\n            self.badges[sk] = badge"),
    # 5. step 循环加 step_idx
    ('            for step in st["steps"]:\n                sn = step["name"]',
     '            step_idx = 0\n            for step in st["steps"]:\n                sn = step["name"]'),
    # 6. gv.addLayout(sv) 改为放入 grid
    ("                gv.addLayout(sv)\n\n                form = QGridLayout()",
     "                sv_w = QWidget()\n                sv_w.setLayout(sv)\n"
     "                _r = 1 + step_idx // self.step_columns\n"
     "                _c = step_idx % self.step_columns\n"
     "                gv.addWidget(sv_w, _r, _c)\n"
     "                step_idx += 1\n\n                form = QGridLayout()"),
]


def main():
    print("=" * 60)
    print("patch_ui_columns — 子环多列布局")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "step_columns" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_cols")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    ok = 0
    for i, (a, b) in enumerate(CHANGES, 1):
        if a not in text:
            print(f"[失败] 改动{i} 锚点未找到")
            continue
        text = text.replace(a, b, 1)
        print(f"✔ 改动{i}")
        ok += 1

    if ok == 0:
        print("\n[中止] 没有一处改动成功，文件未写回")
        return

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}（成功 {ok}/{len(CHANGES)} 处）")


if __name__ == "__main__":
    main()