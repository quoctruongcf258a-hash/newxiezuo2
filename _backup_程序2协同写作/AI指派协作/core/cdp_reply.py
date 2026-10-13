"""core/cdp_reply.py
尽力而为地从已登录的 AI 网页抓取最新回复（用于 real 模式取回产物）。
- 依赖 websocket-client；缺失则直接返回 None，由 delivery 回退模拟。
- 不做任何破坏性操作，只读 document.body 末尾文本，应用无关、best-effort。
"""
import json
import os
import time
import urllib.request


def _port_for(ai: str):
    try:
        _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg = os.path.join(_ROOT, "config", "ai_apps.json")
        with open(cfg, encoding="utf-8") as f:
            apps = json.load(f)
        for a in apps:
            if a.get("名字") == ai:
                p = a.get("cdp_port")
                return p if isinstance(p, int) else None
    except Exception:
        return None
    return None


def grab_last_reply(ai: str, wait: int = 6):
    try:
        import websocket  # websocket-client
    except Exception:
        return None

    port = _port_for(ai)
    if not port:
        return None

    try:
        tabs = json.loads(urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json", timeout=2).read())
        ws_url = None
        for t in tabs:
            if t.get("type") == "page":
                ws_url = t.get("webSocketDebuggerUrl")
                break
        if not ws_url:
            return None

        ws = websocket.create_connection(ws_url, timeout=4)
        ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        time.sleep(0.5)
        ws.send(json.dumps({
            "id": 2, "method": "Runtime.evaluate",
            "params": {"expression": "document.body.innerText.slice(-2500)"}
        }))
        time.sleep(wait)

        last = None
        for _ in range(25):
            try:
                m = json.loads(ws.recv())
                if m.get("id") == 2 and "result" in m:
                    last = m["result"].get("result", {}).get("value")
            except Exception:
                break
        ws.close()
        if last and isinstance(last, str) and len(last) > 20:
            return last.strip()
    except Exception:
        return None
    return None
