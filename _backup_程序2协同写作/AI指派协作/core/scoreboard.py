"""core/scoreboard.py
AI × 维度 得分矩阵 / 累计均分 / 排行榜 / 冠亚季军 / 末位淘汰。
与《全员网格写作流水线》文档记分榜语义对齐，供程序二复用。
新增：子标准（sub_scores）聚合与优势定位，用于精确识别各 AI 的优势方向。
"""


class Scoreboard:
    def __init__(self):
        self.scores = {}      # ai -> [{"round":int,"dims":{dim:float},"judge":str}, ...]
        self.dim_keys = []
        self.sub_records = {}  # ai -> [{"round":int,"subs":{subkey:float},"judge":str}, ...]
        self.sub_keys = []     # 扁平子标准 key 列表

    def set_dims(self, dims: list):
        self.dim_keys = list(dims)

    def set_subcriteria(self, schema: dict):
        """登记子标准矩阵（维度 -> 子标准列表），生扁平 key "维度·子标准"。"""
        self.sub_keys = [f"{d}·{s}" for d, subs in schema.items() for s in subs]

    def add_scores(self, round_no: int, ai: str, dims: dict, judge: str):
        self.scores.setdefault(ai, []).append(
            {"round": round_no, "dims": dict(dims), "judge": judge})

    def add_extended(self, round_no: int, ai: str, sub_scores: dict, judge: str):
        """记录某 AI 在某轮的子标准分（sub_scores：扁平 key -> float）。"""
        self.sub_records.setdefault(ai, []).append(
            {"round": round_no, "subs": dict(sub_scores), "judge": judge})

    def matrix(self) -> dict:
        """AI × 维度 的均值矩阵。"""
        m = {}
        for ai, recs in self.scores.items():
            agg = {}
            for d in self.dim_keys:
                vals = [r["dims"].get(d) for r in recs if d in r["dims"]]
                agg[d] = round(sum(vals) / len(vals), 2) if vals else 0.0
            m[ai] = agg
        return m

    def ranking(self) -> list:
        """累计均分排行 [(ai, score), ...] 降序。"""
        m = self.matrix()
        totals = [(ai, round(sum(v.values()) / len(v), 2) if v else 0.0)
                  for ai, v in m.items()]
        totals.sort(key=lambda x: -x[1])
        return totals

    def crown(self) -> tuple:
        """返回 (冠军, 亚军, 季军)。"""
        r = self.ranking()
        return (r[0][0] if len(r) > 0 else None,
                r[1][0] if len(r) > 1 else None,
                r[2][0] if len(r) > 2 else None)

    def eliminate(self, ratio: float = 0.34) -> list:
        """末位淘汰名单（至少保留 2 人，避免全淘汰）。"""
        r = self.ranking()
        if len(r) <= 2:
            return []
        k = max(1, int(round(len(r) * ratio)))
        k = min(k, len(r) - 2)
        return [ai for ai, _ in r[-k:]]

    def aggregate_advantages(self, top_k: int = 3) -> dict:
        """按子标准聚合各 AI 均值，定位优势方向。

        返回 {
          "per_ai_top": {ai: [(subkey, mean), ... top_k]},
          "global_leader": {subkey: (ai, mean)},
        }
        - per_ai_top：每个 AI 最擅长的 top_k 个子标准（回答"哪些方向有明确优势"）；
        - global_leader：每个子标准全局均值最高的 AI（回答"谁在哪个方向最强"）。
        """
        per_ai = {}
        for ai, recs in self.sub_records.items():
            agg = {}
            for k in self.sub_keys:
                vals = [r["subs"].get(k) for r in recs if k in r["subs"]]
                agg[k] = round(sum(vals) / len(vals), 2) if vals else 0.0
            per_ai[ai] = agg

        top = {ai: sorted(agg.items(), key=lambda x: -x[1])[:top_k]
               for ai, agg in per_ai.items()}

        global_leader = {}
        for k in self.sub_keys:
            best_ai, best_v = None, -1.0
            for ai, agg in per_ai.items():
                v = agg.get(k, 0.0)
                if v > best_v:
                    best_v, best_ai = v, ai
            if best_ai is not None:
                global_leader[k] = (best_ai, best_v)
        return {"per_ai_top": top, "global_leader": global_leader}
