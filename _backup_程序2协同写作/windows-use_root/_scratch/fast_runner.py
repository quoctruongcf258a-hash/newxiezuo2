import time
import json
import os
import pyperclip
import pyautogui

def run_fast_pipeline(prompt_text, save_file_path, app_name="Antigravity"):
    coords_file = os.path.join(os.path.dirname(__file__), "ai_coords.json")
    if not os.path.exists(coords_file):
        print(f"❌ 错误：未找到坐标文件 ai_coords.json，请先运行 record_coords.py 录制坐标！")
        return False

    with open(coords_file, "r", encoding="utf-8") as f:
        coords_data = json.load(f)

    if app_name not in coords_data:
        print(f"❌ 错误：坐标数据中未录制 [{app_name}]，请重新运行 record_coords.py！")
        return False

    info = coords_data[app_name]
    input_x, input_y = info["input_pos"]
    send_x, send_y = info["send_pos"]
    reply_x, reply_y = info["reply_pos"]

    print(f"🚀 开始通过极速坐标驱动 [{app_name}] 执行任务...")

    # 1. 点击输入框
    pyautogui.click(input_x, input_y)
    time.sleep(0.3)

    # 2. 将 Prompt 复制到剪贴板并粘贴
    pyperclip.copy(prompt_text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)

    # 3. 点击发送按钮或按 Enter
    pyautogui.click(send_x, send_y)
    print(f"✅ [{app_name}] 已发送指令，等待 AI 生成回复中...")

    # 4. 等待生成完成（根据需求等待 15 秒）
    time.sleep(15)

    # 5. 点击回复区域并复制内容
    pyautogui.click(reply_x, reply_y)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)

    result_text = pyperclip.paste()
    if result_text:
        os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
        with open(save_file_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        print(f"🎉 [{app_name}] 执行成功！产出已保存至: {save_file_path}")
        return True
    else:
        print(f"⚠️ 警告：未能成功复制到 [{app_name}] 的回复内容。")
        return False

if __name__ == "__main__":
    print("Fast runner module ready.")
