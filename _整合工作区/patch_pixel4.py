import re
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_pixel4")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

NEW = '''def is_ai_busy_pixel(ai):
    """像素判定。支持 mode=point（单点）和 mode=region（区域统计）。
    返回 True/False/None（None=未配置或取色失败）。
    """
    cfg = _load_pixel_cfg()
    entry = cfg.get(ai)
    if not entry:
        return None

    mode = entry.get("mode", "point")

    if mode == "point":
        x, y = entry.get("x"), entry.get("y")
        if x is None or y is None:
            return None
        rgb = _get_pixel(x, y)
        if rgb is None:
            return None
        r, g, b = rgb
        rules = entry.get("rules") or []
        for rule in rules:
            matched = True
            if "max" in rule:
                mx = rule["max"]
                if not (r <= mx[0] and g <= mx[1] and b <= mx[2]):
                    matched = False
            if "min" in rule:
                mn = rule["min"]
                if not (r >= mn[0] and g >= mn[1] and b >= mn[2]):
                    matched = False
            if "b_min" in rule and b < rule["b_min"]: matched = False
            if "r_max" in rule and r > rule["r_max"]: matched = False
            if "g_max" in rule and g > rule["g_max"]: matched = False
            if "r_min" in rule and r < rule["r_min"]: matched = False
            if "g_min" in rule and g < rule["g_min"]: matched = False
            if matched:
                return bool(rule.get("busy", True))
        return bool(entry.get("default_busy", False))

    if mode == "region":
        reg = entry.get("region")
        if not reg or len(reg) != 4:
            return None
        x0, y0, x1, y1 = reg
        step = entry.get("step", 2)
        stats = _region_stats(x0, y0, x1, y1, step)
        if stats is None:
            return None
        blue, white, dark, gray, total = stats
        rules = entry.get("rules") or []
        for rule in rules:
            matched = True
            if "blue_min" in rule and blue < rule["blue_min"]: matched = False
            if "blue_max" in rule and blue > rule["blue_max"]: matched = False
            if "white_min" in rule and white < rule["white_min"]: matched = False
            if "white_max" in rule and white > rule["white_max"]: matched = False
            if "dark_min" in rule and dark < rule["dark_min"]: matched = False
            if "dark_max" in rule and dark > rule["dark_max"]: matched = False
            if matched:
                return bool(rule.get("busy", True))
        return bool(entry.get("default_busy", False))

    return None


def _region_stats(x0, y0, x1, y1, step=2):
    """区域统计：返回 (blue, white, dark, gray, total) 或 None。"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        hdc = user32.GetDC(0)
        try:
            blue = white = dark = gray = total = 0
            for y in range(int(y0), int(y1) + 1, step):
                for x in range(int(x0), int(x1) + 1, step):
                    c = gdi32.GetPixel(hdc, x, y)
                    total += 1
                    if c == -1:
                        continue
                    r = c & 0xFF
                    g = (c >> 8) & 0xFF
                    b = (c >> 16) & 0xFF
                    if b > 180 and b > r + 30 and b > g + 15:
                        blue += 1
                    elif r > 220 and g > 220 and b > 220:
                        white += 1
                    elif r < 100 and g < 100 and b < 110:
                        dark += 1
                    else:
                        gray += 1
            return blue, white, dark, gray, total
        finally:
            user32.ReleaseDC(0, hdc)
    except Exception:
        return None
'''

pattern = re.compile(r"def is_ai_busy_pixel\(ai\):.*?(?=\ndef |\nclass )", re.DOTALL)
matches = list(pattern.finditer(text))
print(f"找到 {len(matches)} 个 is_ai_busy_pixel 定义")

for m in reversed(matches):
    text = text[:m.start()] + NEW + text[m.end():]

TARGET.write_text(text, encoding="utf-8")
print("[OK] 已替换为 point+region 双模式")
