import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

results = []

@WNDENUMPROC
def enum_callback(hwnd, lparam):
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            if w > 400 and h > 300:
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                try:
                    proc = psutil.Process(pid.value).name()
                except:
                    proc = "Unknown"
                results.append((hwnd, proc, title, rect.left, rect.top, rect.right, rect.bottom))
    return True

user32.EnumWindows(enum_callback, 0)

print(f"=== 找到 {len(results)} 个桌面窗口 ===")
for r in results:
    print(f"HWND: {r[0]} | Proc: {r[1]} | Title: '{r[2]}' | Rect: ({r[3]}, {r[4]}, {r[5]}, {r[6]})")
