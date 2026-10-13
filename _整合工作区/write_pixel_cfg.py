import json
from pathlib import Path

cfg = {
    "_说明": "像素忙闲检测。屏幕物理坐标，窗口移动/分辨率改变后需重测。",
    "CodeBuddy": {
        "x": 1833,
        "y": 864,
        "busy_rgb":  [255, 255, 255],
        "idle_rgb":  [111, 113, 129],
        "tolerance": 40
    }
}

path = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\pixel_busy.json")
path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("已写入：", path)
