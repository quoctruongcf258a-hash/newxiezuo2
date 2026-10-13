import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_pixel")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

# 在 is_ai_busy 函数之前插入 pixel 检测辅助函数
MARKER = "def is_ai_busy(ai):"

INSERT = '''# ── 像素忙闲检测（对 CDP 判定不准的 AI 用）──
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


def _get_pixel(x, y):
    """取屏幕物理像素颜色，返回 (r, g, b)。"""
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
    """像素判定：忙/闲/未知。返回 True/False/None。"""
    cfg = _load_pixel_cfg()
    entry = cfg.get(ai)
    if not entry:
        return None
    x, y = entry.get("x"), entry.get("y")
    if x is None or y is None:
        return None
    busy = entry.get("busy_rgb") or [255, 255, 255]
    idle = entry.get("idle_rgb") or [111, 113, 129]
    tol = entry.get("tolerance", 40)
    rgb = _get_pixel(x, y)
    if rgb is None:
        return None
    r, g, b = rgb
    def _near(c):
        return abs(r - c[0]) <= tol and abs(g - c[1]) <= tol and abs(b - c[2]) <= tol
    if _near(busy):
        return True
    if _near(idle):
        return False
    return None


'''

if INSERT.strip() not in text:
    text = text.replace(MARKER, INSERT + MARKER, 1)
    print("[OK] 已插入 pixel 辅助函数")
else:
    print("[SKIP] 已存在，跳过")

# 在 is_ai_busy 函数开头，加 CodeBuddy pixel 优先分支
OLD_START = '''def is_ai_busy(ai):
    """检测 AI 是否正在生成/有排队任务。True=忙，False=空闲。"""
    info = _lookup(ai)'''

NEW_START = '''def is_ai_busy(ai):
    """检测 AI 是否正在生成/有排队任务。True=忙，False=空闲。"""
    # 像素优先（对 CodeBuddy 这类 DOM 判定不准的）
    _px = is_ai_busy_pixel(ai)
    if _px is not None:
        return _px
    info = _lookup(ai)'''

if OLD_START in text and "is_ai_busy_pixel(ai)" not in text.split("def is_ai_busy(ai)")[1][:200]:
    text = text.replace(OLD_START, NEW_START, 1)
    print("[OK] is_ai_busy 已加 pixel 优先分支")
else:
    print("[SKIP] pixel 分支已存在或没匹配到")

TARGET.write_text(text, encoding="utf-8")
print("完成")
