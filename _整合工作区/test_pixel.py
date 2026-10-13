import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy_pixel, _get_pixel
from mix_send import _load_pixel_cfg

cfg = _load_pixel_cfg()
print("配置：", cfg.get("CodeBuddy"))

r, g, b = _get_pixel(1833, 864)
print(f"当前像素：({r},{g},{b})")
print(f"is_ai_busy_pixel('CodeBuddy') = {is_ai_busy_pixel('CodeBuddy')}")
print()
print("手动操作：")
print("  空闲时跑 → 应该返回 False")
print("  打字后发任务 → 立刻再跑 → 应该返回 True")
