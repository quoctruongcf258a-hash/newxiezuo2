"""core/blind_review_format.py
盲审回复格式规范（八维 × 子标准评分卡）+ 方法一/二 解析与落盘。三程序共享（竞赛/协同/蒸馏）。

八维权威定义取自 windows-use/_scratch/rank_dims.py：
    兼容 / 结构 / 衔接 / 角色 / 创意 / 节奏 / 文笔 / 落地
每个维度下设可考量子标准（EXTENDED_SCHEMA），共 22 项，用于精确定位各 AI 的优势方向。

方法一：prompt 强制严格 JSON 评分卡（八维 scores + sub_scores 子标准扁平 key）+ validate 校验 + 偏离重发。
方法二：parse_any 启发式解析任意回复（正则提取「维度:分数」「子标准:分数」+ 优缺点建议）。
"""
import os
import re
import json

# ---------- 八维权威定义 ----------
DIMS = ["兼容", "结构", "衔接", "角色", "创意", "节奏", "文笔", "落地"]

# 扩展子维度（22 项可考量子标准），扁平 key = "维度·子标准"
EXTENDED_SCHEMA = {
    "兼容": ["设定自洽", "人设一致", "前文承接"],
    "结构": ["开篇钩子", "叙事推进", "详略配比"],
    "衔接": ["场景/时空连贯", "过渡自然"],
    "角色": ["动机合理", "声音辨识", "弧光/成长"],
    "创意": ["点子新颖", "意象质量", "反转力度"],
    "节奏": ["张弛控制", "信息密度"],
    "文笔": ["句式与修辞", "语感统一", "零硬伤"],
    "落地": ["可推进性", "指导性", "情绪落点"],
}
SUB_KEYS = [f"{d}·{s}" for d, subs in EXTENDED_SCHEMA.items() for s in subs]

SCORE_MIN, SCORE_MAX = 1.0, 10.0
DEFAULT_SCORE = 7.0

JUDGE_PROMPT_TMPL = """你是一位严格的文学评审，正在对一篇匿名作品进行盲审。
请仅依据作品质量，按以下维度各打 1-10 分（可含一位小数），并给出优点、缺点与修改建议。

评分维度：{dims}

作品编号：{anon_id}
作品内容：
----
{text}
----

请严格按如下 JSON 格式输出，除 JSON 外不要输出任何额外内容（不要解释、不要 ``` 代码块标记）：
{{
  "scores": {{ {score_tmpl} }},
  "pros": ["优点1", "优点2"],
  "cons": ["缺点1", "缺点2"],
  "suggestion": "总体修改建议...",
  "comment": "总体评价..."{sub}
}}
"""


def build_judge_prompt(anon_id, text, dims, extended=True):
    """方法一：注入严格 JSON 评分卡模板。extended=True 时要求输出 sub_scores（22 子标准扁平 key）。"""
    dims_line = "、".join(dims)
    score_tmpl = ", ".join(f'"{d}": 分数(1-10)' for d in dims)
    sub = ""
    if extended:
        items = ", ".join(f'"{k}": 分数(1-10)' for k in SUB_KEYS)
        sub = (",\n  \"sub_scores\": { " + items + " }")
    return JUDGE_PROMPT_TMPL.format(
        dims=dims_line, anon_id=anon_id, text=text[:3500],
        score_tmpl=score_tmpl, sub=sub)


def _clip(x):
    try:
        x = float(x)
    except Exception:
        return DEFAULT_SCORE
    return max(SCORE_MIN, min(SCORE_MAX, x))


def _extract_json(raw):
    if not raw:
        return None
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def validate(raw, dims):
    """方法一校验：八维 scores 齐全（JSON 或文本出现全部维度名）。sub_scores 不强制（避免重发风暴）。"""
    if not raw or not raw.strip():
        return False
    d = _extract_json(raw)
    if isinstance(d, dict):
        sc = d.get("scores")
        if isinstance(sc, dict) and all(dim in sc for dim in dims):
            return True
    return all(dim in raw for dim in dims)


def _card_from_json(raw, dims):
    d = _extract_json(raw) or {}
    sc = d.get("scores", {}) if isinstance(d, dict) else {}
    scores, missing = {}, []
    for dim in dims:
        v = sc.get(dim)
        if v is None:
            scores[dim] = DEFAULT_SCORE
            missing.append(dim)
        else:
            scores[dim] = _clip(v)
    # 子标准分（扁平 key）
    sub_raw = (d.get("sub_scores") or {}) if isinstance(d, dict) else {}
    sub_scores = {}
    for k in SUB_KEYS:
        v = sub_raw.get(k)
        sub_scores[k] = _clip(v) if v is not None else DEFAULT_SCORE
    sub_missing = [k for k in SUB_KEYS if sub_scores[k] == DEFAULT_SCORE]
    return {
        "scores": scores,
        "sub_scores": sub_scores,
        "pros": d.get("pros") if isinstance(d.get("pros"), list) else [],
        "cons": d.get("cons") if isinstance(d.get("cons"), list) else [],
        "suggestion": d.get("suggestion") or "",
        "comment": d.get("comment") or "",
        "missing": missing,
        "sub_missing": sub_missing,
        "source": "strict",
    }


def _extract_sections(raw):
    """从文本提取 优点 / 缺点 / 建议 段落（best-effort）。"""
    def grab(labels):
        for lab in labels:
            m = re.search(rf"【?{re.escape(lab)}】?\s*[:：]?\s*\n(.*?)(?=\n\s*【|$)",
                          raw, re.S)
            if not m:
                m = re.search(rf"【?{re.escape(lab)}】?\s*[:：]?\s*(.*?)(?=\n\s*【|$)",
                              raw, re.S)
            if m:
                block = m.group(1).strip()
                items = [x.strip(" -–·\t") for x in re.split(r"\n|；|;", block)
                         if x.strip(" -–·\t")]
                if items:
                    return items
        return []
    pros = grab(["优点", "亮点", "长处", "优势"])
    cons = grab(["缺点", "不足", "瑕疵", "短板"])
    sug = grab(["建议", "修改意见", "总评", "改进"])
    return pros, cons, ("；".join(sug) if sug else "")


def _parse_sub_any(raw, sub_scores):
    """方法二：从文本用子标准名正则提取分数。"""
    for k in SUB_KEYS:
        _, sname = k.split("·", 1)
        m = re.search(rf"{re.escape(sname)}\s*[:：]\s*(\d+(?:\.\d+)?)", raw)
        if not m:
            m = re.search(rf"{re.escape(sname)}[^\d]{{0,12}}?(\d+(?:\.\d+)?)", raw)
        if m:
            sub_scores[k] = _clip(m.group(1))


def parse_any(raw, dims):
    """方法二：启发式解析任意回复，提取八维 + 子标准分数 + 优缺点建议。"""
    scores, missing = {}, []
    for dim in dims:
        m = re.search(rf"{re.escape(dim)}\s*[:：]\s*(\d+(?:\.\d+)?)", raw)
        if not m:
            m = re.search(rf"{re.escape(dim)}[^\d]{{0,12}}?(\d+(?:\.\d+)?)", raw)
        if m:
            scores[dim] = _clip(m.group(1))
        else:
            scores[dim] = DEFAULT_SCORE
            missing.append(dim)
    sub_scores = {k: DEFAULT_SCORE for k in SUB_KEYS}
    _parse_sub_any(raw, sub_scores)
    sub_missing = [k for k in SUB_KEYS if sub_scores[k] == DEFAULT_SCORE]
    pros, cons, suggestion = _extract_sections(raw)
    return {
        "scores": scores,
        "sub_scores": sub_scores,
        "pros": pros,
        "cons": cons,
        "suggestion": suggestion,
        "comment": "",
        "missing": missing,
        "sub_missing": sub_missing,
        "source": "lenient",
    }


def acquire_review(ai, anon_id, text, dims, dispatch_fn, extended=True,
                   max_retry=2, log_fn=print, read_fn=None):
    """组合入口：方法一（强格式 + dispatch + validate，失败重试强调格式）→ 方法二兜底。

    - 每次尝试：dispatch 发送盲审 prompt（强格式），优先用 read_fn 精确读取最新回复；
    - validate 通过则按 JSON 解析成八维卡（strict，尽力解析 sub_scores）；
    - 不通过且未达上限：记日志并强调格式合规后重发；
    - 全部超限：用最后一份原始文本走 parse_any 启发式兜底（lenient）。
    任何异常都不抛出，最终返回一个含八维 scores 与 sub_scores 的 card。
    """
    last_raw = ""
    for attempt in range(max_retry + 1):
        prompt = build_judge_prompt(anon_id, text, dims, extended=extended)
        try:
            res = dispatch_fn(ai, prompt, dry_run=False)
            raw = (res.get("text", "") or "") if isinstance(res, dict) else ""
        except Exception:
            raw = ""
        if read_fn:
            try:
                latest = read_fn(ai, wait=8)
                if latest:
                    raw = latest
            except Exception:
                pass
        last_raw = raw
        if validate(raw, dims):
            return _card_from_json(raw, dims)
        if attempt < max_retry and log_fn:
            log_fn(f"  · 裁判[{ai}] 第{attempt + 1}次回复格式不符，强调格式合规后重发")
    if log_fn:
        log_fn(f"  · 裁判[{ai}] 方法一超限，改用方法二启发式解析兜底")
    return parse_any(last_raw or "", dims)


def save_review(ai, anon_id, card, out_dir):
    """统一格式落盘：md + json。返回 (md_path, json_path)。"""
    os.makedirs(out_dir, exist_ok=True)
    safe = lambda s: re.sub(r"[\\/:*?\"<>|]", "_", str(s))
    base = f"{safe(ai)}__{safe(anon_id)}"

    md = [f"# 盲审评分卡 · {ai} → {anon_id}", ""]
    md.append("## 八维评分")
    md.append("| 维度 | 分数 |")
    md.append("| --- | --- |")
    for dim, v in card.get("scores", {}).items():
        md.append(f"| {dim} | {v} |")
    miss = card.get("missing") or []
    if miss:
        md.append(f"\n> 缺失维度（已用默认分 {DEFAULT_SCORE} 补齐）：{', '.join(miss)}")

    md.append("\n## 子标准评分（22 项）")
    md.append("| 子标准 | 分数 |")
    md.append("| --- | --- |")
    for k, v in card.get("sub_scores", {}).items():
        md.append(f"| {k} | {v} |")
    sub_miss = card.get("sub_missing") or []
    if sub_miss:
        md.append(f"\n> 缺失子标准（已用默认分 {DEFAULT_SCORE} 补齐）：{len(sub_miss)} 项")

    pros = card.get("pros") or []
    cons = card.get("cons") or []
    sug = card.get("suggestion") or ""
    com = card.get("comment") or ""
    if com:
        md.append(f"\n## 总体评价\n{com}")
    if pros:
        md.append("\n## 优点\n" + "\n".join(f"- {p}" for p in pros))
    if cons:
        md.append("\n## 缺点\n" + "\n".join(f"- {c}" for c in cons))
    if sug:
        md.append(f"\n## 建议\n{sug}")
    md.append(f"\n---\n来源：{card.get('source', '?')}")
    md_path = os.path.join(out_dir, base + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    json_path = os.path.join(out_dir, base + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"ai": ai, "anon_id": anon_id, **card},
                  f, ensure_ascii=False, indent=2)
    return md_path, json_path
