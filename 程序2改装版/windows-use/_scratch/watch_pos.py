import pyautogui, time
print("实时监控鼠标位置（Ctrl+C 停止）")
print("把鼠标移到目标点，记下坐标\n")
try:
    while True:
        p = pyautogui.position()
        print(f"X={p.x:4d}  Y={p.y:4d}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    p = pyautogui.position()
    print(f"\n\n最终位置: X={p.x}  Y={p.y}")
