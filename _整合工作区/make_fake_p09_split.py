import json
from pathlib import Path

# 造一个假的 P09 split.json 用于测试 P10 的拆分引擎
d = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test\01_规划\全书结构")
d.mkdir(parents=True, exist_ok=True)
fake = {
    "拆分维度": "卷",
    "环节": "P09",
    "环节名": "全书结构",
    "列表": [
        {"key": "卷1", "name": "崛起", "start": 1, "end": 50, "note": "主角觉醒"},
        {"key": "卷2", "name": "争霸", "start": 51, "end": 100, "note": "势力扩张"},
        {"key": "卷3", "name": "封神", "start": 101, "end": 150, "note": "终局决战"}
    ]
}
(d / "split.json").write_text(json.dumps(fake, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已造：{d / 'split.json'}")
