import time
import json
import os
import pyautogui
import pyperclip

def record_ui_coordinates():
    print("=" * 60)
    print("    多 AI 窗口界面坐标快捷录制器 (极速定位版)")
    print("=" * 60)
    print("使用说明：")
    print("1. 将要录制的 AI 窗口（如 Antigravity / Bionic / Coze / Trae 等）摆在屏幕上。")
    print("2. 按照提示，将鼠标指针【悬停】在对应位置上，按 Enter 键录制。")
    print("=" * 60)

    ai_apps = ["Antigravity", "Bionic", "Coze", "Namiwork", "Qoder", "TraeWork"]
    coords_data = {}

    for app in ai_apps:
        print(f"\n👉 正在录制 [{app}] 的控件坐标（如果未开启该软件，直接输入 s 跳过）：")
        skip = input(f"是否录制 {app}？(按 Enter 开始录制，输入 s 跳过): ").strip().lower()
        if skip == 's':
            continue
        
        app_info = {}
        
        # 1. 录制输入框坐标
        input(f"【1/3】请把鼠标指针移到 [{app}] 的【输入框】上，然后按 Enter 键记录坐标...")
        pos_input = pyautogui.position()
        app_info["input_pos"] = [pos_input.x, pos_input.y]
        print(f"  ✅ 输入框坐标: X={pos_input.x}, Y={pos_input.y}")
        
        # 2. 录制发送按钮坐标
        input(f"【2/3】请把鼠标指针移到 [{app}] 的【发送按钮】（或输入框内）上，然后按 Enter 键记录坐标...")
        pos_send = pyautogui.position()
        app_info["send_pos"] = [pos_send.x, pos_send.y]
        print(f"  ✅ 发送按钮坐标: X={pos_send.x}, Y={pos_send.y}")
        
        # 3. 录制回复正文复制区坐标
        input(f"【3/3】请把鼠标指针移到 [{app}] 的【AI 回复正文区域】上，然后按 Enter 键记录坐标...")
        pos_reply = pyautogui.position()
        app_info["reply_pos"] = [pos_reply.x, pos_reply.y]
        print(f"  ✅ 回复区域坐标: X={pos_reply.x}, Y={pos_reply.y}")
        
        coords_data[app] = app_info

    output_path = os.path.join(os.path.dirname(__file__), "ai_coords.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(coords_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"🎉 录制完成！坐标配置文件已保存至: {output_path}")
    print("=" * 60)
    input("按 Enter 键退出程序...")

if __name__ == "__main__":
    record_ui_coordinates()
