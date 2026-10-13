import time, json, os
import pyautogui

# (存盘用的key, 提示名, 窗口标题关键词)
AI_APPS = [
    ("CodeBuddy",  "CodeBuddy  (标题: Agents)",               "Agents"),
    ("QUEST",      "QUEST  (标题: Quest Window)",             "Quest Window"),
    ("Doubao",     "Doubao  (标题: 木叶：开局…)",             "木叶"),
    ("Qianwen",    "Qianwen  (标题: 千问)",                   "千问"),
    ("TRAE",       "TRAE  (标题: TraeWork CN [管理员])",      "TraeWork"),
    ("WorkBuddy",  "WorkBuddy  (标题: WorkBuddy)",            "WorkBuddy"),
    ("ZCode",      "ZCode  (标题: ZCode)",                    "ZCode"),
]

def record_ui_coordinates():
    print("=" * 60)
    print("    七人赛马 · 坐标录制器")
    print("=" * 60)
    print("规则：")
    print("  1. 先把 7 个窗口都拉出来摆好，不要最小化。")
    print("  2. 按提示把鼠标【悬停】在目标位置，按 Enter 记录。")
    print("  3. 未开的窗口输入 s 跳过。")
    print("  4. 录完前不要移动/缩放窗口！")
    print("=" * 60)

    coords_data = {}

    for key, hint, title in AI_APPS:
        print(f"\n===== 录制 [{key}]  {hint} =====")
        skip = input(f"  按 Enter 开始；s 跳过：").strip().lower()
        if skip == 's':
            continue

        info = {"window_title": title}

        input(f"  [1/3] 把鼠标移到 [{key}] 的【输入框】上 → Enter")
        p = pyautogui.position()
        info["input_pos"] = [p.x, p.y]
        print(f"      ✅ 输入框: {p.x}, {p.y}")

        input(f"  [2/3] 把鼠标移到 [{key}] 的【发送按钮】上 → Enter")
        p = pyautogui.position()
        info["send_pos"] = [p.x, p.y]
        print(f"      ✅ 发送按钮: {p.x}, {p.y}")

        input(f"  [3/3] 把鼠标移到 [{key}] 的【回复正文区】上 → Enter")
        p = pyautogui.position()
        info["reply_pos"] = [p.x, p.y]
        print(f"      ✅ 回复区: {p.x}, {p.y}")

        coords_data[key] = info

    out = os.path.join(os.path.dirname(__file__), "ai_coords.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(coords_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"🎉 完成！{len(coords_data)} 个窗口已录")
    print(f"   保存: {out}")
    print("=" * 60)
    input("按 Enter 退出...")

if __name__ == "__main__":
    record_ui_coordinates()