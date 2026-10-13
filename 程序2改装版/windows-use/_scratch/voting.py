# voting.py — 终审投票的统计与「问题定位卡」校验
#
# 用户定下的判定规则（四程序每个出口都要走一遍）：
#   · 过半通过 → 放行到下一个程序
#   · 未过半   → 按块打回重做
#   · 平票     → 交叉提意见 + 综合改稿 → 再投（上限 2 轮，仍平票转人工裁决）
#
# 硬规则：反对票必须附「问题定位卡」四件套，缺任一件即为无效票，不计入统计。
#   ① locator  问题出在哪（程序 › 环节 › 卷 › 章 › 六要素段位 › 场景 › 段）
#   ② clause   哪一条出了问题（引用标准条目原文或编号）
#   ③ quote    正文关键句（原样可搜的字串）+ keywords（2—4 个唯一检索词）
#   ④ fix      修改建议（改法方向 + 改动范围）
#
# 投票 JSON 约定（各 AI 输出）：
#   {
#     "voter": "kimi",
#     "verdict": "pass" | "fail",
#     "reason": "一句话总评",
#     "issues": [ { "locator":..., "clause":..., "quote":..., "keywords":[...], "fix":... } ]
#   }

import json
from pathlib import Path

REQUIRED_FIELDS = ("locator", "clause", "quote", "fix")

# 定位卡① 必须细到「段」级，否则不算有效定位
LOCATOR_MIN_SEGMENTS = 4


def load_vote_file(p: Path):
    """读单个投票文件，容忍 AI 夹带解释文字（自动抠 JSON）。"""
    if not p.exists():
        return None
    raw = p.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        pass
    # 退一步：抠出第一个 { 到最后一个 }
    i, j = raw.find("{"), raw.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(raw[i:j + 1])
        except Exception:
            return None
    return None


def check_issue(issue: dict):
    """校验一张问题定位卡，返回 (是否有效, 缺件说明)。"""
    if not isinstance(issue, dict):
        return False, "定位卡不是对象"
    missing = []
    for f in REQUIRED_FIELDS:
        v = issue.get(f)
        if v is None or (isinstance(v, str) and not v.strip()):
            missing.append(f)
    loc = str(issue.get("locator", ""))
    if len([s for s in loc.replace("/", "›").split("›") if s.strip()]) < LOCATOR_MIN_SEGMENTS:
        missing.append("locator(层级不足)")
    if missing:
        return False, "缺：" + "、".join(missing)
    return True, ""


def tally(votes: list):
    """统计投票。

    返回：
      pass_n / fail_n / invalid_n   有效票计数（invalid 为缺件反对票）
      total                         有效票总数
      verdict                       "pass" | "fail" | "tie" | "insufficient"
      issues                        所有有效反对票里的定位卡（已标注来源投票人）
      notes                         统计过程中的说明（如无效票原因）
    """
    pass_n = fail_n = invalid_n = 0
    issues, notes = [], []
    for v in votes:
        if not isinstance(v, dict):
            continue
        who = v.get("voter") or v.get("key") or "?"
        verdict = str(v.get("verdict", "")).strip().lower()
        if verdict in ("pass", "通过", "ok", "yes", "通过票"):
            pass_n += 1
        elif verdict in ("fail", "不通过", "ng", "no", "反对"):
            raw_issues = v.get("issues") or []
            good = []
            for it in raw_issues:
                ok, why = check_issue(it)
                if ok:
                    good.append(it)
                else:
                    notes.append(f"{who} 的问题定位卡无效（{why}），该条已弃用。")
            if good:
                fail_n += 1
                for it in good:
                    it = dict(it)
                    it["_by"] = who
                    issues.append(it)
            else:
                invalid_n += 1
                notes.append(f"{who} 投了反对票但未附有效的问题定位卡 → 该票无效，不计入统计。")
        else:
            notes.append(f"{who} 的票没有可识别的 verdict 字段，已忽略。")

    total = pass_n + fail_n
    if total == 0:
        verdict = "insufficient"
    elif pass_n * 2 > total:
        verdict = "pass"
    elif fail_n * 2 > total:
        verdict = "fail"
    else:
        verdict = "tie"

    return {
        "pass_n": pass_n, "fail_n": fail_n, "invalid_n": invalid_n,
        "total": total, "verdict": verdict,
        "issues": issues, "notes": notes,
    }


def format_issues(issues: list) -> str:
    """把定位卡整理成回改用的文本（喂给写手/润色 AI）。"""
    if not issues:
        return "（无有效反对意见）"
    out = []
    for i, it in enumerate(issues, 1):
        kw = it.get("keywords") or []
        kw_s = "、".join(kw) if isinstance(kw, list) else str(kw)
        out.append(
            f"[{i}] 由 {it.get('_by', '?')} 提出\n"
            f"    ① 位置：{it.get('locator', '')}\n"
            f"    ② 命中条目：{it.get('clause', '')}\n"
            f"    ③ 正文关键句：{it.get('quote', '')}"
            + (f"（检索词：{kw_s}）" if kw_s else "") + "\n"
            f"    ④ 修改建议：{it.get('fix', '')}"
        )
    return "\n".join(out)


def summarize(res: dict) -> str:
    """一行摘要，便于日志。"""
    return (f"通过 {res['pass_n']} / 不通过 {res['fail_n']}"
            f"（无效票 {res['invalid_n']}）→ 判定：{res['verdict']}")


# ──────────────────────────────── 自测 ────────────────────────────────
if __name__ == "__main__":
    demo = [
        {"voter": "kimi", "verdict": "pass", "reason": "整体达标"},
        {"voter": "gemini", "verdict": "fail", "issues": [
            {"locator": "写作 › 正文 › 第3卷 › 第57章 › 动 › 场景2 › 第4-7段",
             "clause": "sixElements 红线「动≠成」",
             "quote": "剑未出鞘，那人的头已经落了",
             "keywords": ["剑未出鞘", "头已经落了"],
             "fix": "第4—7段合并为2段，删中间3句环境描写"}]},
        {"voter": "doubao", "verdict": "fail", "issues": [
            {"locator": "第57章", "clause": "节奏不好", "quote": "", "fix": "建议优化"}]},
        {"voter": "tongyi", "verdict": "pass"},
    ]
    r = tally(demo)
    print(summarize(r))
    for n in r["notes"]:
        print("  note:", n)
    print()
    print(format_issues(r["issues"]))
