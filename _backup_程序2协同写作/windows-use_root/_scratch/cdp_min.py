import json, urllib.request, sys

def list_tabs(port=9222):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
        return json.load(f)

if __name__ == "__main__":
    try:
        tabs = list_tabs()
    except Exception as e:
        print("❌ 连不上 9222:", e); sys.exit(1)
    print(f"发现 {len(tabs)} 个标签页：\n")
    for i, t in enumerate(tabs):
        if t.get("type") != "page": continue
        print(f"[{i}] {t.get('title','?')[:50]}")
        print(f"    URL: {t.get('url','?')[:80]}")
        print(f"    WS : {t.get('webSocketDebuggerUrl','')[:90]}\n")
