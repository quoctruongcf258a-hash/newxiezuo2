# scoreboard.py — 赛马记分榜（用户新增机制）
#
# 用户定下的规则：
#   · 每个大环节最后的审核者（终审闸的投票官们），在投票之外，还要给本次参战的所有 AI
#     做最终结果的打分评估和统计——看谁的哪个环节做得好。
#   · 筛选出最优的、淘汰最差的：以后就用不着最差的参与了。
#   · 以后就知道用谁写哪个环节最好了（环节×AI 的最佳对照表）。
#   · 评估出冠、亚、季军。
#
# 数据来源（三路）：
#   ① 终审打分  ：终审投票官在 vote JSON 里附带 scores（给除自己外每位参战 AI 打 1—10 分）
#   ② 拼接采纳  ：拼接者每拼一块，在产出末尾留 <!--ADOPT: 块ID=产出者--> 标记
#   ③ 参与登记  ：编排器在每个环节记下谁真的写了哪块（participation）
#
# 存储：work/scoreboard.json（单文件，人也可读可改）

import json
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
BOARD = BASE / "work" / "scoreboard.json"
CFG = BASE / "apps.json"

# ──────────────────────────────── 底层 ────────────────────────────────

def _load():
    if BOARD.exists():
        try:
            return json.loads(BOARD.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"records": [], "adoptions": [], "participation": {}, "eliminated": {}}


def _save(b):
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    BOARD.write_text(json.dumps(b, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _rules():
    """从 apps.json 读记分/淘汰/冠亚季军规则。"""
    try:
        d = json.loads(CFG.read_text(encoding="utf-8"))
        sb = d.get("scoreboard") or {}
        el = sb.get("elimination") or {}
        cr = sb.get("crown") or {}
        return {
            "bottomStreak": int(el.get("consecutiveTimes", 3)),
            "bottomLine": float(el.get("scoreBelow", 6.0)),
            "minRounds": int(cr.get("minRounds", 2)),
        }
    except Exception:
        return {"bottomStreak": 3, "bottomLine": 6.0, "minRounds": 2}


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _key(program, chapter, gate):
    return f"{program}|{chapter or '-'}|{gate}"


# ──────────────────────────────── 登记 ────────────────────────────────

def note_participation(program, phase, writer_key):
    """登记：某 AI 在某环节真的产出过内容。"""
    b = _load()
    k = f"{program}|{phase}"
    b.setdefault("participation", {}).setdefault(k, {})
    b["participation"][k][writer_key] = b["participation"].get(k, {}).get(writer_key, 0) + 1
    _save(b)


def record_adoptions(program, chapter, phase, pairs):
    """登记拼接采纳：pairs = [(chunk_id, writer_key), ...]。"""
    if not pairs:
        return
    b = _load()
    for chunk, writer in pairs:
        b["adoptions"].append({"ts": _now(), "program": program, "chapter": chapter or "",
                               "phase": phase, "chunk": chunk, "writer": writer})
    _save(b)


def parse_adopt_markers(text):
    """从拼接产物里抠采纳标记：<!--ADOPT: 块ID=产出者-->。"""
    out = []
    for seg in text.split("<!--ADOPT:")[1:]:
        seg = seg.split("-->", 1)[0].strip()
        if "=" in seg:
            chunk, writer = seg.split("=", 1)
            out.append((chunk.strip(), writer.strip()))
    return out


def record_gate(program, chapter, gate, round_no, votes, verdict):
    """登记一轮终审打分。

    votes：终审票列表，每票可带 scores = [{"ai":..., "score":8.5, "comment":...}]。
    规则：不给自己的产出打分（自己给自己打的分剔除）；没参与该程序的 AI 不打分。
    返回本轮统计摘要 dict。
    """
    b = _load()
    per = {}        # ai -> [score,...]（跨投票官取均值）
    comments = {}
    for v in votes or []:
        if not isinstance(v, dict):
            continue
        voter = v.get("voter") or "?"
        for s in (v.get("scores") or []):
            if not isinstance(s, dict):
                continue
            ai = str(s.get("ai", "")).strip()
            try:
                sc = float(s.get("score"))
            except (TypeError, ValueError):
                continue
            if not ai or ai == voter:
                continue                      # 不给自己打分
            per.setdefault(ai, []).append(max(0.0, min(10.0, sc)))
            if s.get("comment"):
                comments.setdefault(ai, []).append(str(s["comment"])[:80])

    avg = {ai: sum(v) / len(v) for ai, v in per.items() if v}
    bottom = min(avg, key=avg.get) if avg else None

    rec = {"ts": _now(), "program": program, "chapter": chapter or "", "gate": gate,
           "round": round_no, "verdict": verdict,
           "scores": {k: round(v, 2) for k, v in avg.items()},
           "raw": {k: [round(x, 2) for x in v] for k, v in per.items()},
           "comments": comments, "bottom": bottom}
    b["records"].append(rec)

    # ── 垫底淘汰判定（只在最终通过轮记连败） ──
    notes = []
    rules = _rules()
    if bottom and verdict == "pass":
        el = b.setdefault("eliminated", {})
        prog_state = b.setdefault("byProgram", {}).setdefault(program, {})
        st = prog_state.setdefault(bottom, {"consecBottom": 0})
        st["consecBottom"] = st.get("consecBottom", 0) + 1
        # 其他人连败清零
        for ai, s2 in prog_state.items():
            if ai != bottom:
                s2["consecBottom"] = 0
        if avg[bottom] < rules["bottomLine"]:
            if st["consecBottom"] >= rules["bottomStreak"]:
                if not el.get(bottom):
                    el[bottom] = {"program": program, "ts": _now(),
                                  "reason": f"在「{program}」连续 {st['consecBottom']} 次垫底"
                                            f"（均分 {avg[bottom]:.1f} < {rules['bottomLine']}）"}
                    notes.append(f"⛔「{bottom}」已触发淘汰：{el[bottom]['reason']}。"
                                 f"以后默认不再让它参战（scoreboard.py restore {bottom} 可解除）。")
        else:
            st["consecBottom"] = 0

    _save(b)
    rec["notes"] = notes
    return rec


# ──────────────────────────────── 统计 ────────────────────────────────

def _final_records(b):
    """每个 (程序|章|闸) 只取最后一轮的记录。"""
    best = {}
    for r in b.get("records", []):
        k = _key(r["program"], r["chapter"], r["gate"])
        if k not in best or r.get("round", 0) >= best[k].get("round", 0):
            best[k] = r
    return list(best.values())


def stats(program=None):
    """按 AI 聚合：轮数 / 均分 / 最高 / 最低 / 采纳次数 / 连败。"""
    b = _load()
    rules = _rules()
    out = {}
    for r in _final_records(b):
        if program and r["program"] != program:
            continue
        for ai, sc in (r.get("scores") or {}).items():
            s = out.setdefault(ai, {"rounds": 0, "scores": [], "adopted": 0,
                                    "programs": {}})
            s["rounds"] += 1
            s["scores"].append(sc)
            s["programs"].setdefault(r["program"], []).append(sc)
    for a in b.get("adoptions", []):
        if program and a["program"] != program:
            continue
        out.setdefault(a["writer"], {"rounds": 0, "scores": [], "adopted": 0,
                                     "programs": {}})["adopted"] += 1
    for ai, s in out.items():
        v = s["scores"]
        s["avg"] = round(sum(v) / len(v), 2) if v else None
        s["best"] = max(v) if v else None
        s["worst"] = min(v) if v else None
        s["consecBottom"] = b.get("byProgram", {}).get(program, {}).get(ai, {}) \
            .get("consecBottom", 0) if program else 0
        s["eliminated"] = b.get("eliminated", {}).get(ai)
    return out


def crown(program=None):
    """冠亚季军：均分排名，轮数不足 minRounds 无排名资格；被淘汰者无资格。"""
    rules = _rules()
    b = _load()
    el = b.get("eliminated") or {}
    rows = [(ai, s) for ai, s in stats(program).items()
            if s["avg"] is not None and s["rounds"] >= rules["minRounds"]
            and ai not in el]
    rows.sort(key=lambda x: (-x[1]["avg"], -x[1]["adopted"]))
    return rows[:3]


def best_at(program=None):
    """环节×AI 最佳对照表：按采纳次数 + 该环节打分排名。"""
    b = _load()
    table = {}
    for a in b.get("adoptions", []):
        if program and a["program"] != program:
            continue
        k = f"{a['program']} › {a['phase']}"
        t = table.setdefault(k, {})
        t[a["writer"]] = t.get(a["writer"], 0) + 1
    return {k: sorted(t.items(), key=lambda x: -x[1]) for k, t in
            sorted(table.items())}


# ──────────────────────────────── 展示 ────────────────────────────────

def show(program=None):
    st = stats(program)
    if not st:
        print(f"（{'程序「%s」' % program if program else '全部程序'}暂无记分数据）")
        return
    rows = sorted(st.items(), key=lambda x: (-(x[1]["avg"] or 0), -x[1]["adopted"]))
    print(f"{'AI':<14}{'轮数':>4}{'均分':>7}{'最高':>6}{'最低':>6}{'采纳':>5}  备注")
    print("-" * 60)
    for ai, s in rows:
        note = ""
        if s["eliminated"]:
            note = f"⛔ 已淘汰（{s['eliminated']['reason']}）"
        elif s["consecBottom"]:
            note = f"⚠ 连败 {s['consecBottom']} 次"
        print(f"{ai:<14}{s['rounds']:>4}{s['avg'] or '-':>7}{s['best'] or '-':>6}"
              f"{s['worst'] or '-':>6}{s['adopted']:>5}  {note}")


def show_crown(program=None):
    rows = crown(program)
    tag = f"程序「{program}」" if program else "全场"
    if not rows:
        print(f"（{tag}暂无冠亚季军——每 AI 至少跑满 {_rules()['minRounds']} 轮才有资格）")
        return
    medals = ["🥇 冠军", "🥈 亚军", "🥉 季军"]
    print(f"—— {tag} 冠亚季军 ——")
    for (ai, s), m in zip(rows, medals):
        print(f"  {m}：{ai}（均分 {s['avg']}，{s['rounds']} 轮，被采纳 {s['adopted']} 次）")


def show_best_at(program=None):
    t = best_at(program)
    if not t:
        print("（暂无采纳数据——拼接者拼完块并留 ADOPT 标记后生成）")
        return
    print("—— 环节 × AI 最佳对照表（按被采纳次数）——")
    for k, rows in t.items():
        top = "、".join(f"{ai}×{n}" for ai, n in rows[:3])
        print(f"  {k}：<-{top}")


def restore(ai_key):
    b = _load()
    if ai_key in b.get("eliminated", {}):
        del b["eliminated"][ai_key]
        for st in (b.get("byProgram") or {}).values():
            if ai_key in st:
                st[ai_key]["consecBottom"] = 0
        _save(b)
        print(f"✔ 已解除「{ai_key}」的淘汰标记。")
    else:
        print(f"「{ai_key}」不在淘汰名单里。")


def reset():
    _save({"records": [], "adoptions": [], "participation": {}, "eliminated": {}})
    print("✔ 记分榜已清空。")


# ──────────────────────────────── CLI ────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "show"
    if cmd == "show":
        show(args[1] if len(args) > 1 else None)
        print()
        show_crown(args[1] if len(args) > 1 else None)
        print()
        show_best_at(args[1] if len(args) > 1 else None)
    elif cmd == "crown":
        show_crown(args[1] if len(args) > 1 else None)
    elif cmd == "best":
        show_best_at(args[1] if len(args) > 1 else None)
    elif cmd == "restore":
        if len(args) > 1:
            restore(args[1])
        else:
            print("用法：scoreboard.py restore <ai_key>")
    elif cmd == "reset":
        reset()
    else:
        print("用法：scoreboard.py [show|crown|best|restore|reset] [program/ai]")
