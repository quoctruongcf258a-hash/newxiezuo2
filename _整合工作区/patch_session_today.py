# patch_session_today.py — resolve() 优先用 today.json 的 opened 作为参战名单
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\session.py")


def main():
    print("=" * 60)
    print("patch_session_today")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_UI_EXPORT_MODE" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_today")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 在 opened = {...} 之后插入 UI 导出模式分支
    anchor = '    opened = {x["key"]: x for x in (today.get("opened") or [])}\n'
    insert = anchor + '''
    # _UI_EXPORT_MODE：UI 导出的 today.json 里已有 opened 时，直接以它为准
    # （弃用 roster.selection.global，只看"运行中的 AI"）
    if today.get("opened"):
        wanted = [x["key"] for x in today["opened"]]
        layer = "ui_export"
        # 跳过下面"roster 名单 ∩ today"的交集过滤
        skip_intersect = True
    else:
        skip_intersect = False
'''
    if anchor not in text:
        print("[失败] 锚点未找到：opened = {...}")
        return
    text = text.replace(anchor, insert, 1)
    print("✔ 已插入 UI 导出模式分支")

    # 修改交集过滤，加上 skip_intersect 判断
    old_filter = '    if strict_today and opened:\n'
    new_filter = '    if strict_today and opened and not skip_intersect:\n'
    if old_filter in text:
        text = text.replace(old_filter, new_filter, 1)
        print("✔ 交集过滤已加 skip_intersect 开关")
    else:
        print("[警告] 交集过滤锚点未找到（可能已被改）")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()