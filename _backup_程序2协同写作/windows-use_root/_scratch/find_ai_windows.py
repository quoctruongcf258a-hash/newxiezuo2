import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

target_procs = {
    "antigravity.exe": "Antigravity",
    "bionic.exe": "Bionic",
    "coze.exe": "Coze",
    "namiwork.exe": "Namiwork",
    "qoder.exe": "Qoder",
    "qodercn.exe": "QoderCN",
    "trae solo cn.exe": "TraeWork",
    "zcode.exe": "ZCode"
}

found = []

def enum_windows():
    def callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                try:
                    p = psutil.Process(pid.value)
                    p_name = p.name().lower()
                    if p_name in target_procs:
                        rect = wintypes.RECT()
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        w = rect.right - rect.left
                        h = rect.bottom - rect.top
                        if w > 300 and h > 200:
                            found.append({
                                "key": target_procs[p_name],
                                "process": p_name,
                                "pid": pid.value,
                                "hwnd": hwnd,
                                "title": title,
                                "rect": (rect.left, rect.top, rect.right, rect.bottom)
                            })
                except Exception:
                    pass
        return True

    cb = WNDENUMPROC(callback)
    user32.EnumWindows(cb, 0)

    print(f"=== 找到匹配的 AI 窗口 ({len(found)} 个) ===")
    for idx, item in enumerate(found, 1):
        print(f"{idx}. [{item['key']}] '{item['title']}' | PID: {item['pid']} | HWND: {item['hwnd']} | Rect: {item['rect']}")
    return found

if __name__ == "__main__":
    enum_windows()
