# patch_fix_tabs_loop.py — 把分页代码搬进循环（缩进 +4）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_fix_tabs_loop")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    lines = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    # 找起始行：for (_s0, _s1, _suffix) in _pages:
    start = None
    for i, ln in enumerate(lines):
        if "for (_s0, _s1, _suffix) in _pages:" in ln:
            start = i
            break
    if start is None:
        print("[失败] 找不到 for (_s0, _s1, _suffix) in _pages: 行")
        return

    # 找结束行：self.tabs.addTab(container, ...)
    end = None
    for j in range(start, len(lines)):
        if "self.tabs.addTab(container," in lines[j]:
            end = j
            break
    if end is None:
        print("[失败] 找不到 self.tabs.addTab(container, ...)")
        return

    print(f"定位：start={start+1}（for 行），end={end+1}（addTab 行）")

    # 备份
    bak = TARGET.with_suffix(".py.bak_tabloop")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 从 start 行之后开始，到 end 行结束，中间的行全部 +4 缩进
    # 但 start 行本身（for 语句）不动；start 之后第一行是"原本应该在循环内"的 panel 行
    # 关键：从 for 行的**下一行**开始加缩进（跳过 for 行本身）
    # 但 for 后面紧跟的 if/else 已经缩进 4 了（在 for 里面），所以从 panel.run_callback 开始加

    # 找 panel.run_callback 那一行（在 for 循环体之后，缩进 12 空格）
    prc = None
    for k in range(start, end + 1):
        if "panel.run_callback = " in lines[k]:
            prc = k
            break
    if prc is None:
        print("[失败] 找不到 panel.run_callback 行")
        return

    print(f"定位：panel.run_callback 在 {prc+1} 行")

    # 从 prc 到 end（含），每行前加 4 空格
    new_lines = []
    for i, ln in enumerate(lines):
        if prc <= i <= end:
            if ln.strip():     # 非空行加缩进
                new_lines.append("    " + ln)
            else:
                new_lines.append(ln)
        else:
            new_lines.append(ln)

    TARGET.write_text("".join(new_lines), encoding="utf-8")
    print(f"\n✔ 已把 {prc+1}—{end+1} 行（{end-prc+1} 行）缩进 +4，搬进循环")
    print(f"✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()