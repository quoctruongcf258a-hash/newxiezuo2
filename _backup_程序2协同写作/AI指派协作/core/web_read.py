"""core/web_read.py
增强网页读取（替代/补充 core/cdp_reply）：精确读取指定 web AI 对话页的「最新回复」文本。

- 多标签挑选正确的对话页（按 ai_apps.json 的 url/名字 匹配），拒绝非内容页，无匹配返回 None；
- 启发式识别最新回复 DOM 容器（覆盖 kimi / DeepSeek 网页版等），best-effort；
- 接口 grab_latest(ai, wait=8, selectors=None) -> str|None，失败返回 None，绝不阻塞。

复用 cdp_reply._port_for 与 websocket 范式；不修改 cdp_reply 既有接口。
"""
import json
import os
import re
import time
import urllib.request

try:
    from cdp_reply import _port_for as _cdp_port_for
except Exception:  # cdp_reply 不可用时回退到本地等价实现
    _cdp_port_for = None


# 默认候选选择器（覆盖 DeepSeek / kimi / 通用对话容器），依次尝试取最后一条
_DEFAULT_SELECTORS = [
    '[class*="ds-assistant-message-main-content"]',  # DeepSeek 专用（实测）
    '[class*="ds-message"]:last-of-type',            # DeepSeek 消息块
    '[role="assistant"]:last-of-type',
    '[data-role="assistant"]:last-of-type',
    '[class*="assistant"]:last-of-type',
    '.message:last-child',
    '[class*="message"]:last-child',
    '.chat-bubble:last-child',
    '#message-list > *:last-child',
    '.conversation > *:last-child',
]


def _local_port_for(ai):
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


def _port_for(ai):
    if _cdp_port_for is not None:
        p = _cdp_port_for(ai)
        if p:
            return p
    return _local_port_for(ai)


def _apps_entry(ai):
    try:
        _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg = os.path.join(_ROOT, "config", "ai_apps.json")
        with open(cfg, encoding="utf-8") as f:
            apps = json.load(f)
        for a in apps:
            if a.get("名字") == ai:
                return a
    except Exception:
        return None
    return None


def _pick_tab(tabs, ai):
    """挑选正确的对话页：必须 URL 命中目标主机名，拒绝非内容页（edge:///file:// 等）。

    找不到匹配的对话页时返回 None（绝不返回无关页，避免误读文件/界面导致解析全默认）。
    """
    entry = _apps_entry(ai)
    url_kw = ""
    if entry:
        u = entry.get("url", "") or ""
        m = re.search(r"https?://([^/]+)", u)
        url_kw = m.group(1) if m else ""
    name_kw = ai
    candidates = []
    for t in tabs:
        if t.get("type") != "page":
            continue
        u = (t.get("url") or "").lower()
        if any(u.startswith(p) for p in ("edge://", "file://", "about:",
                                         "chrome://", "chrome-extension://",
                                         "devtools://", "data:")):
            continue
        candidates.append(t)
    if url_kw:
        for t in candidates:
            if url_kw.lower() in (t.get("url") or "").lower():
                return t
    for t in candidates:
        if name_kw and name_kw.lower() in (t.get("title") or "").lower():
            return t
    return None


def grab_latest(ai, wait=8, selectors=None):
    """尽力读取 ai 对话页最新回复文本；任何异常返回 None。

    selectors: 自定义候选选择器列表；默认覆盖 kimi/DeepSeek 等网页版。
    返回正文经 .strip()，长度不足 20 视为无效返回 None。
    """
    port = _port_for(ai)
    if not port:
        return None
    sels = selectors or _DEFAULT_SELECTORS
    try:
        tabs = json.loads(urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json", timeout=2).read())
        tab = _pick_tab(tabs, ai)
        if not tab:
            return None
        ws_url = tab.get("webSocketDebuggerUrl")
        if not ws_url:
            return None

        import websocket  # 延迟导入，缺依赖时直接回退
        ws = websocket.create_connection(ws_url, timeout=4)
        ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        time.sleep(0.3)

        expr = (
            "(()=>{"
            "const sels=" + json.dumps(sels) + ";"
            "for(const s of sels){try{const e=document.querySelectorAll(s);"
            "if(e&&e.length){const t=e[e.length-1].innerText;"
            "if(t&&t.trim().length>20)return t;}}catch(_){}}"
            "const b=document.body?document.body.innerText:'';"
            "return b?b.slice(-3000):'';})()"
        )

        def _eval():
            ws.send(json.dumps({
                "id": 2, "method": "Runtime.evaluate",
                "params": {"expression": expr, "returnByValue": True}}))
            last = None
            for _ in range(25):
                try:
                    m = json.loads(ws.recv())
                    if m.get("id") == 2 and "result" in m:
                        last = m["result"].get("result", {}).get("value")
                except Exception:
                    break
            return last

        time.sleep(wait)
        first = _eval()
        time.sleep(2)
        second = _eval()
        ws.close()
        cand = first or ""
        if second and len(second) > len(cand):
            cand = second
        if cand and len(cand.strip()) > 20:
            return cand.strip()
    except Exception:
        return None
    return None
