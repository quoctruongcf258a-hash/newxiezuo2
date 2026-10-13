import json
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
data = json.loads(p.read_text(encoding="utf-8"))

# 全部 51 个环节的专家抬头
role_map = {
    # 规划阶段
    "P01": "网文项目策划顾问",
    "P02": "网文市场分析师",
    "P03": "文风设计师",
    "P04": "故事核心提炼师",
    "P05": "主题策划与文案师",
    "P06": "人物设定师",
    "P07": "冲突设计师",
    "P08": "世界观架构师",
    "P0Z-1": "势力架构师",
    "P0Z-2": "副本任务设计师",
    "P0Z-3": "血脉灵兽设定师",
    "P0Z-4": "地图场景设计师",
    "P0Z-5": "宝物传承设计师",
    "P0Z-6": "对手体系设计师",
    "P09": "小说结构规划师",
    "P10": "分卷结构规划师",
    "P11": "情绪节奏规划师",
    "P12": "叙事节奏规划师",
    "P13": "结局设计师",
    "P14": "全书总纲规划师",
    "P15": "剧情粗纲师",
    "P16": "章节细纲师",
    "P17": "详细细纲师",
    "P18": "章纲规划师",
    "P19": "开篇爆破专家",
    "P20": "伏笔线索管理师",
    "P21": "书名策划师",
    "P22": "简介文案师",
    "P23": "标签策略师",
    "P24": "封面策划师",
    "P25": "项目文档管理员",
    "P26": "发布合规顾问",
    "P27": "规划质检官",
    # 写作阶段
    "02-01": "细纲分析师",
    "02-02": "章节对齐师",
    "02-03": "分镜设计师",
    "02-04": "网文写手",
    "02-05": "节奏自检师",
    # 去AI阶段
    "03-01": "网文润色师",
    # 审核阶段
    "04-01": "逻辑一致性审核官",
    "04-02": "平台合规审核官",
    "04-03": "爽点节奏审核官",
    "04-04": "文风格式审核官",
    "04-05": "质检汇总官",
    "04-06": "成书检验官",
    "04-07": "低级错误检查官",
    "04-08": "入库管理员",
    "04-09": "剧情推演师",
    # 出厂阶段
    "05-01": "出厂低级错误检查员",
    "05-02": "名称章号统一员",
    "05-03": "定稿归档员",
}

count = 0
for phase_key, phase_data in data.items():
    if not isinstance(phase_data, dict):
        continue
    rings = phase_data.get("环节")
    if not isinstance(rings, list):
        continue
    for ring in rings:
        code = ring.get("code")
        if code in role_map:
            ring["expert_role"] = role_map[code]
            count += 1

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ 已为 {count} 个环节写入 expert_role")
