import pyautogui, json, os, time

WS = r"C:\mai\multi-ai-pipeline\windows-use"
FP = os.path.join(WS, "ai_coords.json")

print("=" * 60)
print("重录「Doubao」的输入框坐标（实际窗口=TraeWork）")
print("=" * 60)
print("1. 把 TraeWork 窗口摆好、可见")
print("2. 鼠标移到它的【输入框中间】")
print("3. 按 Enter")
input("准备好了按 Enter...")

p = pyautogui.position()
c = json.load(open(FP, encoding="utf-8"))
c["Doubao"]["input_pos"] = [p.x, p.y]
c["Doubao"]["window_title"] = "TraeWork CN"
c["Doubao"]["real_proc"] = "TRAE SOLO CN"
json.dump(c, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n✅ Doubao 新坐标: {p.x}, {p.y}")

# 顺便看 TraeWork 窗口 rect，算相对坐标
import pygetwindow as gw
for w in gw.getAllWindows():
    if "TraeWork" in w.title:
        rx = (p.x - w.left) / w.width
        ry = (p.y - w.top) / w.height
        c["Doubao"]["input_rel"] = [round(rx,4), round(ry,4)]
        c["Doubao"]["window_rect"] = [w.left, w.top, w.width, w.height]
        json.dump(c, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"   窗口: [{w.title}]  ({w.left},{w.top} {w.width}x{w.height})")
        print(f"   相对: ({rx:.3f}, {ry:.3f})")
        break
