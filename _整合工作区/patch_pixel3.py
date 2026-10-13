import re
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_pixel3")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

# 新的函数体（支持 rules 格式）
NEW_FUNC = '''def is_ai_busy_pixel(ai):
    """像素判定。返回 True/False/None（None=未配置或取色失败）。"""
    cfg = _load_pixel_cfg()
    entry = cfg.get(ai)
    if not entry:
        return None
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
'''

# 找到所有 is_ai_busy_pixel 定义，替换为新的
pattern = re.compile(
    r"def is_ai_busy_pixel\(ai\):.*?(?=\ndef |\nclass )",
    re.DOTALL,
)

matches = list(pattern.finditer(text))
print(f"找到 {len(matches)} 个 is_ai_busy_pixel 定义")

# 从后往前替换，避免位置偏移
for m in reversed(matches):
    text = text[:m.start()] + NEW_FUNC + text[m.end():]

TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已替换全部 {len(matches)} 个定义为新 rules 格式")
