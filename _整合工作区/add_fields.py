# add_fields.py — 给"全书结构/总纲/粗纲/简短/详细"5 个环单独定义字段
import json
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\环节模板.json")

FIELDS = {
    "P09": ["三幕/五幕划分", "主线弧光", "开局钩子", "中点翻转", "高潮爆点",
            "终局画面", "各卷主线递进关系"],
    "P14": ["故事内容摘要（500 字）", "故事底色", "人物成长", "最后结局"],
    "P15": ["每卷一段话（约 200 字）", "卷级起承转合"],
    "P16": ["章序号", "每章一句话（约 30 字）"],
    "P17": ["章序号", "目标", "阻力", "代价", "时间锚点", "章内跨度",
            "与上章时差", "倒计时状态", "爽点", "叙事线归属", "对手层级",
            "视角", "关键实体", "本章变化", "章末未闭合问题",
            "六要素阶段", "钩子类型"],
}

data = json.loads(TARGET.read_text(encoding="utf-8"))
changed = 0

for r in data.get("固定环", []):
    code = r.get("code")
    if code in FIELDS:
        r["fields"] = FIELDS[code]
        changed += 1
        print(f"  {code} {r['name']} → {len(FIELDS[code])} 个字段")

if changed:
    bak = TARGET.with_suffix(".json.bak_fields")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✔ 已给 {changed} 个环加 fields")
else:
    print("没有变化")