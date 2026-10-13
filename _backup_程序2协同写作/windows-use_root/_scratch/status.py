import json, urllib.request
for port, name in [(9222,"DeepSeek"),(9223,"CodeBuddy"),(9224,"QUEST"),(9225,"Doubao"),(9226,"Qianwen"),(9227,"WorkBuddy"),(9228,"ZCode")]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
        if pages:
            print(f"✅ {name:12} 端口{port}  [{pages[0].get('title','')[:40]}]")
        else:
            print(f"⚠ {name:12} 端口{port}  无页面")
    except:
        print(f"❌ {name:12} 端口{port}  连不上")
