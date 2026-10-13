import json
from pathlib import Path

# ── 配置：项目目录 + 季边界 ──
out_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 尝试读 P10 split.json，如果不存在，用硬编码的季边界
p10_split = out_root / "01_规划" / "分卷结构" / "split.json"
seasons = []

if p10_split.exists():
    try:
        data = json.loads(p10_split.read_text(encoding="utf-8"))
        seasons = data.get("列表") or []
        print(f"[OK] 读 P10 split.json：{len(seasons)} 季")
    except Exception as e:
        print(f"[WARN] P10 split.json 解析失败：{e}")

if not seasons:
    # 硬编码 fallback：150 章，按 30 章一季切
    total_ch = 150
    season_size = 30
    n_season = (total_ch + season_size - 1) // season_size
    for i in range(1, n_season + 1):
        start = (i - 1) * season_size + 1
        end = min(i * season_size, total_ch)
        seasons.append({
            "key": f"季{i}",
            "name": f"季{i}",
            "start": start,
            "end": end,
        })
    print(f"[FALLBACK] 按 30 章/季硬造 {len(seasons)} 季")

# ── 构造 进度.json ──
stages = []
for i, s in enumerate(seasons, start=1):
    stages.append({
        "阶段号": i,
        "起章": s.get("start") or s.get("起章") or 1,
        "止章": s.get("end") or s.get("止章") or 99999,
        "季名": s.get("name") or s.get("key") or f"季{i}",
    })

progress = {
    "项目名": "女王归来_test",
    "总章数": 150,
    "当前阶段": 1,
    "总阶段数": len(stages),
    "阶段列表": stages,
    "已完成阶段": [],
    "当前阶段状态": "进行中",
}

pj = out_root / "进度.json"
pj.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[OK] 已写：{pj}\n")
for s in stages:
    print(f"  阶段{s['阶段号']}  {s['起章']}-{s['止章']}  ({s['季名']})")
