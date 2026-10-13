import json, sys
from pathlib import Path

MAIN_WEIGHTS = {
    "ai_rewrite": 0.125,
    "plot": 0.19,
    "character": 0.15,
    "coherence": 0.16,
    "style": 0.125,
}

SUB_WEIGHTS = {
    "rhythm": 0.05,
    "info": 0.04,
    "scene": 0.03,
    "theme": 0.04,
    "reader": 0.05,
    "sustainability": 0.04,
}

HARD_RULES = {
    "ai_rewrite": 7.0,
}

def decide(main, sub, key_block=False):
    reasons = []
    hard_fail = False

    for k, t in HARD_RULES.items():
        if main.get(k, 0) < t:
            hard_fail = True
            reasons.append(f"{k} < {t}")

    main_total = sum(main.get(k, 0) * w for k, w in MAIN_WEIGHTS.items())
    sub_total = sum(sub.get(k, 0) * w for k, w in SUB_WEIGHTS.items())
    total = round(main_total + sub_total, 2)

    if hard_fail:
        return total, "reject", True, reasons

    pass_line = 8.5 if key_block else 8.0
    if total >= pass_line:
        d = "pass"
    elif total >= 6.8:
        d = "revise"
    else:
        d = "reject"

    return total, d, False, reasons

def main():
    if len(sys.argv) < 2:
        print("用法: python score_review_v3.py review.json")
        return

    p = Path(sys.argv[1])
    data = json.loads(p.read_text(encoding="utf-8-sig"))

    main_scores = data["main_scores"]
    sub_scores = data["sub_scores"]
    key_block = data.get("key_block", False)

    total, decision, hard_fail, reasons = decide(main_scores, sub_scores, key_block)

    data["total_score"] = total
    data["decision"] = decision
    data["hard_fail"] = hard_fail
    data["hard_fail_reasons"] = reasons

    out = p.with_name(p.stem + "_scored.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已输出: {out}")
    print(f"total_score={total}, decision={decision}")

if __name__ == "__main__":
    main()
