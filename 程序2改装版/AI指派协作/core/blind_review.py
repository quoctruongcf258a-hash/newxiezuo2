"""core/blind_review.py
盲审隔离：产物匿名打乱 + 跨厂裁判调度（crossVendorRule）。
裁判必须选自与所有写手不同厂商的 AI，杜绝同源偏置。
"""
import random


def anonymize(entries: list):
    """entries: [(ai, text), ...] -> 打乱顺序、去除作者标识的匿名列表。"""
    items = [{"anon_id": f"作品{i+1}", "ai": ai, "text": text}
             for i, (ai, text) in enumerate(entries)]
    random.shuffle(items)
    return items


def pick_judges(writers: list, vendor_map: dict, n_judges: int = 1):
    """从 vendor_map(名字->厂商) 中选与写手不同厂商的裁判，返回真实 app 名。
    与写手同厂商的、以及写手本人都排除；不足则退回其它非写手 AI。
    """
    writer_vendors = {vendor_map.get(w) for w in writers if w in vendor_map}
    candidates = [k for k in vendor_map
                  if k not in writers and vendor_map.get(k) not in writer_vendors]
    if not candidates:
        candidates = [k for k in vendor_map if k not in writers]
    return candidates[:max(1, n_judges)]


def schedule_reviews(anon_items: list, judges: list):
    """生成 (judge, anon_item) 评审任务列表。"""
    schedule = []
    for j in judges:
        for it in anon_items:
            schedule.append((j, it))
    return schedule
