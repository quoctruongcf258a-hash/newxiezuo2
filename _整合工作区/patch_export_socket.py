# patch_export_socket.py — 导出改用 socket 检测（IPv4 + IPv6）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_export_socket")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_socket_cdp_alive" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_exsock")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 替换上一轮的 HTTP 检测
    old = '''        def _http_cdp_alive(port):
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

    new = '''        def _socket_cdp_alive(port):
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
                   if x.get("启用") is not False
                   and _socket_cdp_alive(x.get("cdp_port"))]
'''

    if old not in text:
        print("[失败] 锚点未找到（上一轮 HTTP 检测代码）")
        return
    text = text.replace(old, new, 1)
    print("✔ 导出逻辑：改用 socket 检测（IPv4+IPv6）")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()