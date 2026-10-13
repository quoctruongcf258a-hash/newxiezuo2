# patch_export_path.py — 修正导出路径
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_export_path")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_path_fixed" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_path")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    old = '''        scratch = os.path.join(os.path.dirname(paths.WINDOWS_USE), "_scratch")
        today_path = os.path.join(scratch, "today.json")
'''
    new = '''        # _path_fixed：导出到 windows-use/_scratch/today.json
        scratch = os.path.join(paths.WINDOWS_USE, "_scratch")
        today_path = os.path.join(scratch, "today.json")
'''

    if old not in text:
        print("[失败] 锚点未找到")
        return
    text = text.replace(old, new, 1)
    print("✔ 导出路径已改为 windows-use\\_scratch\\today.json")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()