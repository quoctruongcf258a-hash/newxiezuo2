import json, urllib.request
for port in [9222, 9223, 9224, 9225, 9226, 9227, 9228]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
        if pages:
            for p in pages[:1]:
                print(f"端口 {port}  [{p.get('title','')[:50]}]  {p.get('url','')[:70]}")
        else:
            print(f"端口 {port}  (无页面)")
    except Exception as e:
        print(f"端口 {port}  连不上")
