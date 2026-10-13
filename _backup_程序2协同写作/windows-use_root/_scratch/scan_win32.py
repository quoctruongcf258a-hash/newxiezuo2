from pywinauto import Desktop

print("=== pywinauto 扫描所有桌面窗口 ===")
windows = Desktop(backend="win32").windows()
for w in windows:
    try:
        t = w.window_text()
        if t and len(t.strip()) > 0:
            rect = w.rectangle()
            print(f"Title: '{t}' | Handle: {w.handle} | Class: {w.class_name()} | Rect: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
    except Exception:
        pass
