import time
import ctypes
import os
import pyperclip
import pyautogui
from ctypes import wintypes

user32 = ctypes.windll.user32

def bring_window_to_top_and_send(hwnd, text_to_send):
    """直接通过代码激活图形界面窗口并发送文本。"""
    try:
        # 1. 还原并置顶窗口
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        time.sleep(0.2)
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)

        # 2. 点击窗口中央确保焦点在输入框
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.3)

        # 3. 将文本复制到剪贴板并粘贴
        pyperclip.copy(text_to_send)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)

        # 4. 按回车发送
        pyautogui.press("enter")
        print(f"✅ 成功通过代码驱动图形界面 (HWND: {hwnd}) 发送指令！")
        return True
    except Exception as e:
        print(f"❌ 驱动图形界面失败: {e}")
        return False

if __name__ == "__main__":
    print("Direct GUI Controller ready.")
