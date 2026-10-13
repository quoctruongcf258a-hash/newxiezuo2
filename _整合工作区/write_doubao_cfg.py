import json
from pathlib import Path

cfg = {
    "_说明": "像素忙闲检测。豆包用单点 (559,565)：深蓝=待发送，深灰=运行中，浅色=空闲。",
    "Doubao": {
        "x": 559,
        "y": 565,
        "rules": [
            {"name": "运行中", "busy": True,  "max": [130, 130, 130]},
            {"name": "待发送", "busy": True,  "b_min": 220, "r_max": 60, "g_max": 130}
        ],
        "default_busy": False
    }
}

path = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\pixel_busy.json")
path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("已写入：", path)
print(json.dumps(cfg, ensure_ascii=False, indent=2))
