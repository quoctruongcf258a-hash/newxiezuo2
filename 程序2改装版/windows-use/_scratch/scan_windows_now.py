import win32gui

def get_visible_windows():
    wins = []
    def enum_cb(hwnd, lparam):
        if win32gui.IsWindowVisible(hwnd):
            txt = win32gui.GetWindowText(hwnd)
            if txt and len(txt.strip()) > 0:
                rect = win32gui.GetWindowRect(hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                if w > 300 and h > 200:
                    wins.append((hwnd, txt, rect))
        return True
    
    win32gui.EnumWindows(enum_cb, None)
    return wins

if __name__ == "__main__":
    w_list = get_visible_windows()
    print(f"=== 当前桌面所有可见大窗口 ({len(w_list)} 个) ===")
    for idx, (h, t, r) in enumerate(w_list, 1):
        print(f"{idx}. HWND: {h} | Title: '{t}' | Rect: {r}")
