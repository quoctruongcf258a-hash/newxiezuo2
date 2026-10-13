import os, json
from PIL import Image
import win32gui, win32ui

ICON_DIR = r"C:\mai\multi-ai-pipeline\ui\icons"
os.makedirs(ICON_DIR, exist_ok=True)

CFG = r"C:\mai\multi-ai-pipeline\config\ai_apps.json"
apps = json.load(open(CFG, encoding="utf-8"))

def extract_icon(exe_path, out_path):
    if not os.path.exists(exe_path):
        return f"exe 不存在"
    try:
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        if not large:
            return "无图标"
        hicon = large[0]
        info = win32gui.GetIconInfo(hicon)
        hbm = info[4]
        if not hbm:
            return "无彩色位图"
        bmp = win32ui.CreateBitmapFromHandle(hbm)
        bi = bmp.GetInfo()
        data = bmp.GetBitmapBits(True)
        img = Image.frombuffer("RGBA", (bi["bmWidth"], bi["bmHeight"]), data, "raw", "BGRA", 0, 1)
        img.save(out_path, "PNG")
        win32gui.DestroyIcon(hicon)
        return f"OK {img.size}"
    except Exception as e:
        return f"失败: {e}"

EDGE_PATHS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"F:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]

for p in apps:
    name = p["名字"]
    exe = p.get("exe")
    if not exe:
        for ep in EDGE_PATHS:
            if os.path.exists(ep):
                exe = ep; break
    if not exe:
        print(f"  {name}: 没有 exe"); continue
    out = os.path.join(ICON_DIR, f"{name}.png")
    r = extract_icon(exe, out)
    print(f"  {name}: {r}")

print(f"\n图标目录: {ICON_DIR}")
print("文件:")
for f in sorted(os.listdir(ICON_DIR)):
    print(f"  {f}")
