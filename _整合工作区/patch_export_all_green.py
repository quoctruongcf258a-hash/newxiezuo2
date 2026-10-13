# patch_export_all_green.py — 导出只看 CDP 通不通，不看启用字段
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_export_all_green")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_all_green_export" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_allgreen")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 替换导出条件：去掉 "启用 is not False"
    old = '''        enabled = [x for x in apps
                   if x.get("启用") is not False
                   and _socket_cdp_alive(x.get("cdp_port"))]
'''
    new = '''        # _all_green_export：只看 CDP 通不通，不看启用字段
        enabled = [x for x in apps
                   if _socket_cdp_alive(x.get("cdp_port"))]
'''

    if old not in text:
        print("[失败] 锚点未找到")
        return
    text = text.replace(old, new, 1)
    print("✔ 导出条件：改为只看 CDP 通不通")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()