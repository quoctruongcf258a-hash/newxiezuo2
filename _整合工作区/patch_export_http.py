# patch_export_http.py — 导出改用 HTTP /json 检测
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_export_http")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_http_cdp_alive" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_exhttp")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 替换上一次的导出逻辑
    old = ('        try:\n'
           '            from players import cdp_alive as _cdp_check\n'
           '        except Exception:\n'
           '            def _cdp_check(_p): return True\n'
           '        enabled = [x for x in apps\n'
           '                   if x.get("启用") is not False\n'
           '                   and _cdp_check(x.get("cdp_port"))]\n')

    new = '''        def _http_cdp_alive(port):
            """HTTP 请求 /json 判断 CDP 端口是否通（比 socket 更稳，兼容 IPv6）。"""
            if not port:
                return False
            import urllib.request
            for host in ("127.0.0.1", "localhost"):
                try:
                    url = f"http://{host}:{port}/json"
                    with urllib.request.urlopen(url, timeout=1) as r:
                        return r.status == 200
                except Exception:
                    continue
            return False

        enabled = [x for x in apps
                   if x.get("启用") is not False
                   and _http_cdp_alive(x.get("cdp_port"))]
'''

    if old not in text:
        print("[失败] 锚点未找到（上一轮补丁的导出逻辑）")
        return
    text = text.replace(old, new, 1)
    print("✔ 导出逻辑：改为 HTTP /json 检测")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()