# patch_fast_cdp.py — CDP 检测改并发 + 缩短超时
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_fast_cdp")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_fast_cdp" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_fastcdp")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 改 _refresh_merge_combo：并发检测
    old = '''        def _alive(port):
            if not port:
                return False
            import socket
            for family, host in ((socket.AF_INET, "127.0.0.1"),
                                  (socket.AF_INET6, "::1")):
                try:
                    s = socket.socket(family, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect((host, port))
                    s.close()
                    return True
                except Exception:
                    continue
            return False

        names = [x.get("名字", "") for x in apps
                 if x.get("名字") and _alive(x.get("cdp_port"))]
'''

    new = '''        # _fast_cdp：并发检测，0.15 秒超时
        def _alive_one(port):
            if not port:
                return False
            import socket
            for family, host in ((socket.AF_INET, "127.0.0.1"),
                                  (socket.AF_INET6, "::1")):
                try:
                    s = socket.socket(family, socket.SOCK_STREAM)
                    s.settimeout(0.15)
                    s.connect((host, port))
                    s.close()
                    return True
                except Exception:
                    continue
            return False

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=18) as _ex:
            _results = list(_ex.map(lambda x: _alive_one(x.get("cdp_port")), apps))
        names = [x.get("名字", "") for x, ok in zip(apps, _results)
                 if x.get("名字") and ok]
'''

    if old not in text:
        print("[失败] 锚点未找到（_refresh_merge_combo 里的 _alive 函数）")
        return
    text = text.replace(old, new, 1)
    print("✔ 已把 _refresh_merge_combo 改成并发检测")

    # 同样改 _export_roster_to_cli 里的 _socket_cdp_alive
    old2 = '''        def _socket_cdp_alive(port):
            """socket 检测 CDP 端口（IPv4 + IPv6 都试），0.3 秒超时。"""
            if not port:
                return False
            import socket
            for family, host in ((socket.AF_INET, "127.0.0.1"),
                                  (socket.AF_INET6, "::1")):
                try:
                    s = socket.socket(family, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect((host, port))
                    s.close()
                    return True
                except Exception:
                    continue
            return False

        enabled = [x for x in apps
                   if _socket_cdp_alive(x.get("cdp_port"))]
'''
    new2 = '''        # _fast_cdp：并发检测，0.15 秒超时
        def _socket_cdp_alive(port):
            if not port:
                return False
            import socket
            for family, host in ((socket.AF_INET, "127.0.0.1"),
                                  (socket.AF_INET6, "::1")):
                try:
                    s = socket.socket(family, socket.SOCK_STREAM)
                    s.settimeout(0.15)
                    s.connect((host, port))
                    s.close()
                    return True
                except Exception:
                    continue
            return False

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=18) as _ex:
            _res = list(_ex.map(lambda x: _socket_cdp_alive(x.get("cdp_port")), apps))
        enabled = [x for x, ok in zip(apps, _res) if ok]
'''
    if old2 in text:
        text = text.replace(old2, new2, 1)
        print("✔ 已把导出逻辑改成并发检测")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()