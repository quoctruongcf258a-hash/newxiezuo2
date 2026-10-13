"""CDP 发送器：向指定 AI 发送指令。5 个已验证，CodeBuddy 走 pyautogui 兜底。"""
import json, urllib.request, websocket, time, sys, os

# 每个 AI 的 (端口, 页面URL关键词)
APPS = {
    "QUEST":     (9224, ""),
    "Doubao":    (9225, ""),
    "Qianwen":   (9226, "qianwen.com"),
    "WorkBuddy": (9227, ""),
    "ZCode":     (9228, ""),
    "DeepSeek":  (9222, "deepseek"),
}

class Tab:
    def __init__(self, port, url_kw=""):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
        target = None
        if url_kw:
            for p in pages:
                if url_kw in p.get("url",""): target = p; break
        if target is None and pages:
            target = pages[0]
        if not target:
            raise Exception(f"端口 {port} 没页面")
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
        self.mid = 0
        self.title = target.get("title","")
    def js(self, code):
        self.mid += 1
        self.ws.send(json.dumps({"id":self.mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid:
                return r.get("result",{}).get("result",{}).get("value")

    def write(self, text):
        return self.js(f"""
        (() => {{
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return "no-input";
            el.focus();
            if (el.tagName === 'TEXTAREA') {{
                const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
                s.call(el, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
            }} else {{
                document.execCommand('insertText', false, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
            }}
            return "ok";
        }})()
        """)

    def enter(self):
        return self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return "no-input";
            el.focus();
            const o = {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true};
            el.dispatchEvent(new KeyboardEvent('keydown', o));
            el.dispatchEvent(new KeyboardEvent('keypress', o));
            el.dispatchEvent(new KeyboardEvent('keyup', o));
            return "ok";
        })()
        """)

    def send_text(self, text):
        w = self.write(text)
        if w != "ok":
            return f"write={w}"
        time.sleep(0.3)
        e = self.enter()
        return f"write=ok enter={e}"


def send(ai_name, text):
    """向指定 AI 发送文字，返回状态"""
    if ai_name not in APPS:
        return f"❌ 未配置: {ai_name}"
    port, kw = APPS[ai_name]
    try:
        t = Tab(port, kw)
        result = t.send_text(text)
        return f"✅ {ai_name} [{t.title[:30]}] {result}"
    except Exception as e:
        return f"❌ {ai_name}: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python cdp_send.py <AI名字> <文字>")
        print("可用:", list(APPS.keys()))
        sys.exit()
    ai = sys.argv[1]
    text = sys.argv[2]
    print(send(ai, text))
