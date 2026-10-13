# session.py — 「今日阵容」会话管理
#
# 解决的问题：你每天打开的 AI 软件不一定一样（网页还是桌面端、装没装、登没登），
# 所以不能让配置写死阵容。本模块把两件事拆开：
#
#   roster.json  候选池（长期）：有哪些可用的 AI、各自的默认形态与网址/路径
#   today.json   今日阵容（每次运行）：今天实际打开了哪几个、分别是什么形态
#
# 运行时由 session.resolve() 合成「实际参战名单」：
#   ① 按四层覆盖取值   global < program（按程序） < phase（按环节） < chapter（按章）
#   ② 与今日实际打开的集合取交集 —— 今天没开的自动剔除并告警
#   ③ 校验：至少 2 人、拼接者在列、跨厂盲审提醒
#
# ── 命令行用法 ────────────────────────────────────────────────
#   python session.py show                          # 看候选池 + 今日阵容
#   python session.py preset slim5                  # 按预设建今日阵容
#   python session.py new doubao:web kimi:web antigravity:desktop
#                                                  # 手工登记今天开了哪些（key:形态）
#   python session.py add gemini:web --target https://gemini.google.com
#   python session.py set doubao --form desktop --target "C:/x/Doubao.exe"
#   python session.py rm kimi
#   python session.py merge yuanbao                 # 指定拼接者
#   python session.py resolve --program 写作 --phase 正文 --chapter 0057
#                                                  # 打印本次实际参战名单（排障用）
#   python session.py draft --program 写作 --chapter 0057
#                                                  # 生成一份可编辑的 today.json 草案
#
# 最省事的日常用法：直接告诉我「今天开了豆包、Kimi、Gemini 网页，还有 Antigravity 桌面端」，
# 我照这句把 today.json 写出来，你双击 run_gui.bat 就能跑。

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROSTER_JSON = HERE / "roster.json"
TODAY_JSON = HERE / "today.json"

FORM_ALIASES = {
    "web": "web", "网页": "web", "网页版": "web", "浏览器": "web",
    "desktop": "desktop", "桌面": "desktop", "桌面端": "desktop",
    "电脑端": "desktop", "程序": "desktop", "客户端": "desktop", "exe": "desktop",
}


# ──────────────────────────────── 读取 ────────────────────────────────

def load_json(p: Path, default=None):
    if not p.exists():
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_roster() -> dict:
    r = load_json(ROSTER_JSON)
    if not r:
        raise SystemExit(f"[错误] 找不到候选池 {ROSTER_JSON}")
    return r


def load_today() -> dict:
    return load_json(TODAY_JSON, default={}) or {}


def save_today(data: dict):
    data["date"] = data.get("date") or date.today().isoformat()
    with open(TODAY_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ──────────────────────────────── 候选池工具 ────────────────────────────────

def registry_index(roster: dict) -> dict:
    return {x["key"]: x for x in roster.get("registry", [])}


def default_form(entry: dict) -> str:
    """从候选池条目推断默认形态：优先 web（免装），没 web 才用 desktop。"""
    ch = entry.get("channel", [])
    if "web" in ch:
        return "web"
    if "desktop" in ch:
        return "desktop"
    if "api" in ch:
        return "web"  # API 走网页通道录入
    return "web"


def normalize_form(s: str) -> str:
    return FORM_ALIASES.get((s or "").strip().lower(), "web")


def make_opened_item(entry: dict, form=None, target=None) -> dict:
    """由候选池条目 + 今日实际形态，合成一个「已打开」条目。"""
    f = normalize_form(form) if form else default_form(entry)
    tgt = target
    if not tgt:
        if f == "desktop":
            tgt = entry.get("desktopTarget") or entry.get("target") or ""
            # 候选池里 desktop 的 target 可能是 exe 路径，也可能是插件描述
        else:
            tgt = entry.get("target") or ""
    return {
        "key": entry["key"],
        "label": entry.get("label", entry["key"]),
        "vendor": entry.get("vendor", ""),
        "region": entry.get("region", ""),
        "form": f,
        "target": tgt,
        "browser": entry.get("browser", "EDGE"),
        "bestFor": entry.get("bestFor", []),
    }


# ──────────────────────────────── 四层覆盖解析 ────────────────────────────────

def _layer(sel: dict, program=None, phase=None, chapter=None):
    """依次返回 命中的层名 与 该层的 key 列表（空列表视为未覆盖）。"""
    steps = []
    if chapter:
        v = (sel.get("perChapter") or {}).get(str(chapter))
        if v:
            steps.append(("chapter", list(v)))
    if phase:
        v = (sel.get("perPhase") or {}).get(phase)
        if v:
            steps.append(("phase", list(v)))
    if program:
        v = (sel.get("program") or {}).get(program)
        if v:
            steps.append(("program", list(v)))
    v = sel.get("global")
    if v:
        steps.append(("global", list(v)))
    return steps


def resolve(roster: dict, today: dict, program=None, phase=None, chapter=None,
            strict_today=True):
    """合成本次实际参战名单。

    返回 dict：
      participants  [app 字典, ...]      实际参战（已按今日交集过滤）
      merge_app     app 字典             拼接者
      layer         命中的覆盖层名
      warnings      [str, ...]           告警（今日未开、跨厂不足、人数不足…）
      excluded      [str, ...]           被今日过滤掉的 key
    """
    reg = registry_index(roster)
    sel = roster.get("selection") or {}
    warnings, excluded = [], []

    steps = _layer(sel, program, phase, chapter)
    layer = steps[0][0] if steps else "global"
    wanted = steps[0][1] if steps else list(sel.get("global") or [])

    opened = {x["key"]: x for x in (today.get("opened") or [])}

    if strict_today and opened:
        keep = []
        for k in wanted:
            if k in opened:
                keep.append(k)
            else:
                excluded.append(k)
                warnings.append(f"「{reg.get(k, {}).get('label', k)}」在名单里，但今天没登记为已打开，已自动剔除。")
        wanted = keep

    # 合成 app 字典
    participants = []
    for k in wanted:
        if k in opened:
            participants.append(dict(opened[k]))
        elif k in reg:
            participants.append(make_opened_item(reg[k]))
        else:
            warnings.append(f"名单里的「{k}」在候选池中不存在，已跳过。")

    # 拼接者：允许两种身份——
    #   (a) 参战成员之一（轮转写手里的一个，符合「全员既写又审」）
    #   (b) 专职拼接者：今日已打开、但不在写手轮转名单里（例：元宝专管拼接）
    merge_key = today.get("merge_app") or sel.get("merge_app") or ""
    pk = [p["key"] for p in participants]
    merge = None
    if merge_key in pk:
        merge = next(p for p in participants if p["key"] == merge_key)
    elif merge_key and merge_key in opened:
        merge = dict(opened[merge_key])
        warnings.append(
            f"拼接者「{merge.get('label')}」不在写手轮转名单内，按【专职拼接者】使用"
            f"（不参与写作与盲审）。")
    elif merge_key and merge_key in reg and not strict_today:
        merge = make_opened_item(reg[merge_key])
        warnings.append(f"拼接者「{merge['label']}」未登记为今日打开，按候选池默认值使用。")
    else:
        if merge_key:
            warnings.append(
                f"拼接者「{merge_key}」既不在参战名单、今天也没登记打开，已回退为第一名"
                f"「{pk[0]}」。" if pk else f"拼接者「{merge_key}」不可用，且当前无参战成员。")
        merge = participants[0] if participants else None

    # 赛马记分榜：已被淘汰的 AI 强行参战要告警
    board_file = HERE / "work" / "scoreboard.json"
    if board_file.exists():
        try:
            el = (json.loads(board_file.read_text(encoding="utf-8"))
                  .get("eliminated") or {})
        except Exception:
            el = {}
        for p in participants:
            if p["key"] in el:
                warnings.append(
                    f"「{p['label']}」已被记分榜淘汰（{el[p['key']].get('reason', '')}），"
                    f"建议从今日名单移除；确要参战可 scoreboard.py restore {p['key']} 解除。")

    # 校验
    if len(participants) < 2:
        warnings.append(
            f"当前只有 {len(participants)} 名参战成员——网格写作至少需要 2 名"
            f"（1 写 1 审）。请再登记至少 1 个今天已打开的 AI。")
    vend = {}
    for p in participants:
        vend.setdefault(p.get("vendor") or p["key"], []).append(p["label"])
    same = {v: ls for v, ls in vend.items() if len(ls) > 1 and v}
    if same and len(vend) == 1:
        warnings.append(
            "参战成员全部来自同一厂商，盲审将失去独立性（同源偏置），"
            "建议再加入至少一个其它厂商的 AI。")
    elif same:
        for v, ls in same.items():
            warnings.append(f"注意：{'、'.join(ls)} 同属「{v}」，互审时视为弱独立。")

    return {
        "participants": participants,
        "merge_app": merge,
        "layer": layer,
        "warnings": warnings,
        "excluded": excluded,
    }


# ──────────────────────────────── 展示 ────────────────────────────────

def cmd_show(_args):
    roster = load_roster()
    today = load_today()
    reg = roster["registry"]
    opened = {x["key"]: x for x in (today.get("opened") or [])}

    print("=" * 78)
    print("候选池（roster.json）—— 共 %d 项，● 表示今天已登记为打开" % len(reg))
    print("=" * 78)
    for e in reg:
        mark = "●" if e["key"] in opened else "○"
        forms = "/".join(e.get("channel", []))
        print(f"  {mark} {e['key']:<14} {e.get('label','') :<18} [{forms}]  {e.get('target','')}")

    print()
    print("=" * 78)
    print("预设阵容（python session.py preset <key> 一键套用）")
    print("=" * 78)
    for p in roster.get("presets", []):
        print(f"  {p.get('key'):<14} {p.get('label','')}")
        print(f"     {', '.join(p.get('participants', []))}   |   拼接者：{p.get('merge_app','')}")

    print()
    print("=" * 78)
    print("今日阵容（today.json）")
    print("=" * 78)
    if not today or not today.get("opened"):
        print("  （尚未登记。用 `python session.py preset slim5` 快速起一套，")
        print("    或直接告诉助手今天开了哪些 AI。）")
        return
    print(f"  日期：{today.get('date')}")
    for x in today["opened"]:
        print(f"  ● {x['key']:<14} {x.get('label','') :<18} {x.get('form')}  {x.get('target','')}")
    print(f"  拼接者：{today.get('merge_app') or '(未指定，用 roster 默认)'}")


def cmd_preset(args):
    roster = load_roster()
    reg = registry_index(roster)
    presets = {p["key"]: p for p in roster.get("presets", [])}
    p = presets.get(args.key)
    if not p:
        print(f"[错误] 没有预设「{args.key}」。可选：")
        for k, v in presets.items():
            print(f"   {k:<10} {v.get('label','')}")
        return
    opened = [make_opened_item(reg[k]) for k in p["participants"] if k in reg]
    save_today({
        "_说明": "今日阵容：本次运行实际打开的 AI。可直接编辑本文件，或用 run_gui.bat 登记。",
        "opened": opened,
        "merge_app": p.get("merge_app", ""),
    })
    print(f"已按预设「{p.get('label')}」建立今日阵容（{len(opened)} 名）：")
    for x in opened:
        print(f"   ● {x['key']:<14} {x['form']:<8} {x['target']}")
    print(f"拼接者：{p.get('merge_app')}")
    print("\n请核对：这些 AI 今天是否真的都开着？形态与路径是否与实际一致？")


def _parse_kv(token: str, reg: dict):
    """解析 `key:form` 形式的登记项。"""
    if ":" in token:
        k, f = token.split(":", 1)
    else:
        k, f = token, None
    k = k.strip()
    if k not in reg:
        print(f"[跳过] 候选池里没有「{k}」")
        return None
    return make_opened_item(reg[k], form=f)


def cmd_new(args):
    roster = load_roster()
    reg = registry_index(roster)
    opened = []
    for tok in args.items:
        it = _parse_kv(tok, reg)
        if it:
            opened.append(it)
    if not opened:
        print("[错误] 没有有效登记项。示例：python session.py new doubao:web kimi:web antigravity:desktop")
        return
    save_today({
        "_说明": "今日阵容：本次运行实际打开的 AI。可直接编辑本文件，或用 run_gui.bat 登记。",
        "opened": opened,
        "merge_app": args.merge or "",
    })
    print(f"今日阵容已建立（{len(opened)} 名）：")
    for x in opened:
        print(f"   ● {x['key']:<14} {x['form']:<8} {x['target']}")
    if args.merge:
        print(f"拼接者：{args.merge}")


def cmd_add(args):
    roster = load_roster()
    reg = registry_index(roster)
    it = _parse_kv(args.key, reg)
    if not it:
        return
    if args.target:
        it["target"] = args.target
    if args.form:
        it["form"] = normalize_form(args.form)
    today = load_today()
    opened = today.get("opened") or []
    opened = [x for x in opened if x["key"] != it["key"]] + [it]
    today["opened"] = opened
    save_today(today)
    print(f"已加入/更新：{it['key']} | {it['form']} | {it['target']}")


def cmd_set(args):
    today = load_today()
    opened = today.get("opened") or []
    hit = None
    for x in opened:
        if x["key"] == args.key:
            hit = x
    if not hit:
        print(f"[错误] 今日阵容里没有「{args.key}」，先用 add 加入。")
        return
    if args.form:
        hit["form"] = normalize_form(args.form)
    if args.target:
        hit["target"] = args.target
    save_today(today)
    print(f"已更新：{hit['key']} | {hit['form']} | {hit['target']}")


def cmd_rm(args):
    today = load_today()
    opened = [x for x in (today.get("opened") or []) if x["key"] != args.key]
    today["opened"] = opened
    save_today(today)
    print(f"已移除「{args.key}」，当前剩 {len(opened)} 名。")


def cmd_merge(args):
    today = load_today()
    today["merge_app"] = args.key
    save_today(today)
    print(f"拼接者已设为「{args.key}」。")


def cmd_resolve(args):
    roster = load_roster()
    today = load_today()
    r = resolve(roster, today, program=args.program, phase=args.phase,
                chapter=args.chapter, strict_today=not args.ignore_today)
    print("=" * 78)
    print(f"本次实际参战（命中覆盖层：{r['layer']}）")
    print("=" * 78)
    for p in r["participants"]:
        print(f"   ● {p['key']:<14} {p['form']:<8} {p.get('label','') :<18} {p.get('target','')}")
    print(f"   拼接者：{(r['merge_app'] or {}).get('key', '(无)')}")
    if r["excluded"]:
        print(f"   因今日未开而剔除：{', '.join(r['excluded'])}")
    if r["warnings"]:
        print("\n告警：")
        for w in r["warnings"]:
            print(f"   ! {w}")


def cmd_draft(args):
    """生成 today.json 草案：把候选池里该程序/该环节会用到的人都列出来，供你划掉没开的。"""
    roster = load_roster()
    reg = registry_index(roster)
    sel = roster.get("selection") or {}
    steps = _layer(sel, args.program, args.phase, args.chapter)
    keys = steps[0][1] if steps else list(sel.get("global") or [])
    opened = [make_opened_item(reg[k]) for k in keys if k in reg]
    if TODAY_JSON.exists() and not args.force:
        print(f"[提示] {TODAY_JSON} 已存在；加 --force 才覆盖。")
        return
    save_today({
        "_说明": "今日阵容草案：请把今天【没有打开】的条目整段删除，再核对形态与路径。",
        "opened": opened,
        "merge_app": sel.get("merge_app", ""),
    })
    print(f"草案已写入 {TODAY_JSON}（{len(opened)} 名）。请删掉今天没开的，核对 target 后即可运行。")


# ──────────────────────────────── 入口 ────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="今日阵容会话管理")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("show", help="查看候选池与今日阵容").set_defaults(func=cmd_show)

    p = sub.add_parser("preset", help="按预设建立今日阵容")
    p.add_argument("key")
    p.set_defaults(func=cmd_preset)

    p = sub.add_parser("new", help="登记今天实际打开的 AI（key:形态）")
    p.add_argument("items", nargs="+")
    p.add_argument("--merge", default="", help="拼接者 key")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("add", help="加入一个 AI")
    p.add_argument("key")
    p.add_argument("--form", default="")
    p.add_argument("--target", default="")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("set", help="改某个 AI 的形态或路径")
    p.add_argument("key")
    p.add_argument("--form", default="")
    p.add_argument("--target", default="")
    p.set_defaults(func=cmd_set)

    p = sub.add_parser("rm", help="移除一个 AI")
    p.add_argument("key")
    p.set_defaults(func=cmd_rm)

    p = sub.add_parser("merge", help="指定拼接者")
    p.add_argument("key")
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("resolve", help="打印本次实际参战名单")
    p.add_argument("--program", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--chapter", default=None)
    p.add_argument("--ignore-today", action="store_true",
                   help="忽略今日登记，按四层覆盖直接出名单")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("draft", help="生成今日阵容草案")
    p.add_argument("--program", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--chapter", default=None)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_draft)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
