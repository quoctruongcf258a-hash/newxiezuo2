# 1. players.py：cdp_alive 改 socket
fp = r"C:\mai\multi-ai-pipeline\ui\players.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

old = '''def cdp_alive(port):
    if not port: return False
    try:
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=1.5) as f:
            return True
    except:
        return False'''

new = '''def cdp_alive(port):
    if not port: return False
    import socket
    s = socket.socket()
    s.settimeout(0.2)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except:
        return False
    finally:
        s.close()'''

if old in t:
    t = t.replace(old, new)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(t)
    print("OK players.py 改 socket")
else:
    print("players.py 没找到目标")

# 2. monitor_panel.py 里也有 cdp_alive
fp2 = r"C:\mai\multi-ai-pipeline\ui\monitor_panel.py"
with open(fp2, "r", encoding="utf-8") as f:
    t2 = f.read()

old2 = '''    def cdp_alive(self, port):
        if not port: return False
        try:
            import urllib.request
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as f:
                return True
        except: return False'''

new2 = '''    def cdp_alive(self, port):
        if not port: return False
        import socket
        s = socket.socket()
        s.settimeout(0.2)
        try:
            s.connect(("127.0.0.1", port))
            return True
        except: return False
        finally:
            s.close()'''

if old2 in t2:
    t2 = t2.replace(old2, new2)
    with open(fp2, "w", encoding="utf-8") as f:
        f.write(t2)
    print("OK monitor_panel.py 改 socket")
else:
    print("monitor_panel.py 没找到目标")
