# patch_export_green.py — 导出只包含"绿灯（CDP 端口通）"的 AI
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_export_green")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_cdp_check" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_exportgreen")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 改：只导运行中的
    a = '        enabled = [x for x in apps if x.get("启用") is not False]\n'
    b = ('        try:\n'
         '            from players import cdp_alive as _cdp_check\n'
         '        except Exception:\n'
         '            def _cdp_check(_p): return True\n'
         '        enabled = [x for x in apps\n'
         '                   if x.get("启用") is not False\n'
         '                   and _cdp_check(x.get("cdp_port"))]\n')

    if a not in text:
        print("[失败] 锚点未找到")
        return
    text = text.replace(a, b, 1)
    print("✔ 导出逻辑：改为只看 CDP 端口通的（绿灯）")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()