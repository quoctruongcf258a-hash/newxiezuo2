import json
from pathlib import Path

cfg = {
    "_说明": "像素忙闲检测。mode=point 单点检测；mode=region 区域统计。",
    "Doubao": {
        "mode": "point",
        "x": 559, "y": 565,
        "rules": [
            {"name": "运行中", "busy": True, "max": [130, 130, 130]},
            {"name": "待发送", "busy": True, "b_min": 220, "r_max": 60, "g_max": 130}
        ],
        "default_busy": False
    },
    "CodeBuddy": {
        "mode": "region",
        "region": [651, 976, 680, 1003],
        "step": 2,
        "rules": [
            {"name": "待发送", "busy": True, "blue_min": 50},
            {"name": "运行中", "busy": True, "white_min": 30}
        ],
        "default_busy": False
    }
}

path = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\pixel_busy.json")
path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("已写入：", path)
print(json.dumps(cfg, ensure_ascii=False, indent=2)[:400], "...")
