import pywinauto
from pywinauto import Desktop

def scan_ai_windows():
    print("=== 正在扫描系统当前打开的 AI 界面窗口 ===")
    desktop = Desktop(backend="uia")
    windows = desktop.windows()
    
    target_keywords = ["antigravity", "bionic", "coze", "namiwork", "qoder", "trae", "zcode"]
    found = []
    
    for w in windows:
        try:
            title = w.window_text()
            if not title:
                continue
            title_lower = title.lower()
            for kw in target_keywords:
                if kw in title_lower:
                    rect = w.rectangle()
                    found.append({
                        "keyword": kw,
                        "title": title,
                        "class_name": w.class_name(),
                        "handle": w.handle,
                        "rect": (rect.left, rect.top, rect.right, rect.bottom)
                    })
                    break
        except Exception as e:
            pass
            
    print(f"找到 {len(found)} 个符合目标的 AI 窗口：")
    for idx, item in enumerate(found, 1):
        print(f"{idx}. [{item['keyword'].upper()}] {item['title']} (Handle: {item['handle']}, Rect: {item['rect']})")

if __name__ == "__main__":
    scan_ai_windows()
