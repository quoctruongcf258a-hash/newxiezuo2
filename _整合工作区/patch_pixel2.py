import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_pixel2")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

# ── 1. 在 is_ai_busy 之前插入 pixel 检测辅助函数 ──
MARKER = "def is_ai_busy(ai):"

INSERT = '''# ── 像素忙闲检测（部分 AI 的 DOM 判定不准，用屏幕像素判定）──
_PIXEL_CFG = None

def _load_pixel_cfg():
    global _PIXEL_CFG
    if _PIXEL_CFG is not None:
        return _PIXEL_CFG
    try:
        import json as _json
        from pathlib import Path as _P
        cfg_path = _P(__file__).parent / "pixel_busy.json"
        if cfg_path.exists():
            _PIXEL_CFG = _json.loads(cfg_path.read_text(encoding="utf-8"))
        else:
            _PIXEL_CFG = {}
    except Exception:
        _PIXEL_CFG = {}
    return _PIXEL_CFG


def _get_screen_pixel(x, y):
    """取屏幕物理像素颜色，返回 (r, g, b) 或 None。"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        hdc = user32.GetDC(0)
        try:
            c = gdi32.GetPixel(hdc, int(x), int(y))
            if c == -1:
                return None
            return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
        finally:
            user32.ReleaseDC(0, hdc)
    except Exception:
        return None


def is_ai_busy_pixel(ai):
    """像素判定。返回 True/False/None（None=未配置该 AI 或取色失败）。"""
    cfg = _load_pixel_cfg()
    entry = cfg.get(ai)
    if not entry:
        return None
    x, y = entry.get("x"), entry.get("y")
    if x is None or y is None:
        return None
    rgb = _get_screen_pixel(x, y)
    if rgb is None:
        return None
    r, g, b = rgb

    rules = entry.get("rules") or []
    for rule in rules:
        matched = True
        # max: r/g/b 都 <= 阈值
        if "max" in rule:
            mx = rule["max"]
            if not (r <= mx[0] and g <= mx[1] and b <= mx[2]):
                matched = False
        # min: r/g/b 都 >= 阈值
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


'''

if "def is_ai_busy_pixel" not in text:
    text = text.replace(MARKER, INSERT + MARKER, 1)
    print("[OK] 已插入 pixel 辅助函数")
else:
    print("[SKIP] pixel 辅助函数已存在")

# ── 2. 在 is_ai_busy 函数开头加 pixel 优先分支 ──
OLD_HEAD = '''def is_ai_busy(ai):
    """检测 AI 是否正在生成/有排队任务。True=忙，False=空闲。"""
    info = _lookup(ai)'''

NEW_HEAD = '''def is_ai_busy(ai):
    """检测 AI 是否正在生成/有排队任务。True=忙，False=空闲。"""
    # 像素优先（对 DOM 判定不准的 AI）
    _px = is_ai_busy_pixel(ai)
    if _px is not None:
        return _px
    info = _lookup(ai)'''

if OLD_HEAD in text and "_px = is_ai_busy_pixel(ai)" not in text:
    text = text.replace(OLD_HEAD, NEW_HEAD, 1)
    print("[OK] is_ai_busy 已加 pixel 优先分支")
else:
    print("[SKIP] pixel 分支已存在或没匹配到")

TARGET.write_text(text, encoding="utf-8")
print("完成")
