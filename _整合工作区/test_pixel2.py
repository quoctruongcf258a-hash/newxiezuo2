import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy_pixel, _get_pixel, _load_pixel_cfg

cfg = _load_pixel_cfg()
print("配置：", cfg.get("Doubao"))
rgb = _get_pixel(559, 565)
print(f"当前像素 (559,565)：{rgb}")
print(f"is_ai_busy_pixel('Doubao') = {is_ai_busy_pixel('Doubao')}")
print()
print("手动操作验证：")
print("  空闲时跑 → 应 False")
print("  打字后跑 → 应 True（待发送）")
print("  发送后跑 → 应 True（运行中）")
