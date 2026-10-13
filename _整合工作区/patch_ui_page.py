# patch_ui_page.py — 环节1 分两页
# 1) assign_panel.py：加 step_slice 参数，只渲染指定范围的子环
# 2) collab_app.py：环节1 拆成两个 tab
import shutil
from pathlib import Path

AP = Path(r"F:\赛马23环整合工作室\程序2改装版\app\assign_panel.py")
CA = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def patch_assign_panel():
    print("\n【1】改 assign_panel.py")
    text = AP.read_text(encoding="utf-8")
    if "step_slice" in text:
        print("  [跳过] 已打过补丁")
        return
    bak = AP.with_suffix(".py.bak_page")
    if not bak.exists():
        shutil.copy(AP, bak)
        print(f"  已备份：{bak.name}")

    changes = [
        ("def __init__(self, with_runner=True, stages=None, columns=1, step_columns=2):",
         "def __init__(self, with_runner=True, stages=None, columns=1, step_columns=2, step_slice=None):"),
        ("        self.step_columns = max(1, int(step_columns))",
         "        self.step_columns = max(1, int(step_columns))\n        self.step_slice = step_slice"),
        ('            step_idx = 0\n            for step in st["steps"]:\n                sn = step["name"]',
         '            step_idx = 0\n'
         '            _all_steps = st["steps"]\n'
         '            if self.step_slice:\n'
         '                _s0, _s1 = self.step_slice\n'
         '                _all_steps = _all_steps[_s0:_s1]\n'
         '            for step in _all_steps:\n'
         '                sn = step["name"]'),
    ]
    ok = 0
    for i, (a, b) in enumerate(changes, 1):
        if a not in text:
            print(f"  [失败] 改动{i} 锚点未找到")
            continue
        text = text.replace(a, b, 1)
        print(f"  ✔ 改动{i}")
        ok += 1
    if ok:
        AP.write_text(text, encoding="utf-8")
        print(f"  已写回（{ok}/{len(changes)}）")


def patch_collab_app():
    print("\n【2】改 collab_app.py")
    text = CA.read_text(encoding="utf-8")
    if "step_slice=(_s0" in text or 'step_slice=(s0, s1)' in text:
        print("  [跳过] 已打过补丁")
        return
    bak = CA.with_suffix(".py.bak_page")
    if not bak.exists():
        shutil.copy(CA, bak)
        print(f"  已备份：{bak.name}")

    # 找到 for i, st in enumerate(sb.PIPELINE, 1): 这一段
    old_head = '        for i, st in enumerate(sb.PIPELINE, 1):\n            panel = AssignPanel(with_runner=False, stages=[st["key"]], step_columns=2)\n'
    if old_head not in text:
        old_head = '        for i, st in enumerate(sb.PIPELINE, 1):\n            panel = AssignPanel(with_runner=False, stages=[st["key"]])\n'
    if old_head not in text:
        print("  [失败] for 循环头部锚点未找到")
        print("  请用记事本打开 collab_app.py，Ctrl+F 搜 'for i, st in enumerate(sb.PIPELINE'，")
        print("  把它后面 2 行贴给我，我改锚点。")
        return

    # 头部替换：拆成 pages
    new_head = '''        for i, st in enumerate(sb.PIPELINE, 1):
            n_steps = len(st["steps"])
            if n_steps > 20:
                half = (n_steps + 1) // 2
                _pages = [(0, half, "(上)"), (half, n_steps, "(下)")]
            else:
                _pages = [(None, None, "")]
            for (_s0, _s1, _suffix) in _pages:
                if _s0 is None:
                    panel = AssignPanel(with_runner=False, stages=[st["key"]], step_columns=2)
                else:
                    panel = AssignPanel(with_runner=False, stages=[st["key"]], step_columns=2, step_slice=(_s0, _s1))
'''
    text = text.replace(old_head, new_head, 1)

    # tab 标题加 suffix
    old_tab = 'self.tabs.addTab(container, f"环节{i} {st[\'label\']}")'
    new_tab = 'self.tabs.addTab(container, f"环节{i} {st[\'label\']}{_suffix}")'
    if old_tab in text:
        text = text.replace(old_tab, new_tab, 1)
        print("  ✔ tab 标题已加后缀")
    else:
        print("  [警告] tab 标题锚点未找到（可能已改过，不影响功能）")

    CA.write_text(text, encoding="utf-8")
    print("  已写回")


def main():
    print("=" * 60)
    print("patch_ui_page — 环节1 分两页")
    print("=" * 60)
    patch_assign_panel()
    patch_collab_app()
    print("\n完成。下一步：重启 UI")


if __name__ == "__main__":
    main()