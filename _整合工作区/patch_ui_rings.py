# patch_ui_rings.py — 让 UI 的 PIPELINE 从 rings_items.json 动态生成
# 三处改动：
#   1. import 后加 _load_rings_items / _build_pipeline_from_rings
#   2. 替换写死的 PIPELINE 为动态版本（读不到时用兜底）
#   3. assign_block / assign_role 支持 list（配合多选按钮）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\stage_board.py")

A1 = ('ROOT = paths.APP_ROOT\n'
      'COLLAB_ROOT = paths.APP_ROOT\n'
      'DEFAULT_PATH = paths.join("work", "collab", "stage_board.json")\n')

B1 = A1 + '''

# ────────────────────────────────────────────────────────────
# 从 rings_items.json 动态生成 PIPELINE（33 环等）
# ────────────────────────────────────────────────────────────
_RING_STAGE_MAP = [
    ("01_规划", "规划", "对当前项目全部规划环做深度完善"),
    ("02_写作", "写作", "章纲 → 正文"),
    ("03_去AI", "去AI", "去 AI 味润色"),
    ("04_审核", "审核", "质检评审"),
    ("05_出厂", "出厂", "上架前低级错误检查"),
]


def _load_rings_items():
    p = paths.join("rules", "rings_items.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _build_pipeline_from_rings():
    rings = _load_rings_items()
    if not rings:
        return None
    out = []
    for stage_key, label, desc in _RING_STAGE_MAP:
        info = rings.get(stage_key, {})
        items = info.get("环节", [])
        if not items:
            continue
        steps = []
        for item in items:
            name = item.get("name") or item.get("code") or "?"
            steps.append({
                "name": name,
                "code": item.get("code", name),
                "norms": False,
                "blocks": ["产出"],
                "mode": item.get("type", "mesh"),
                "desc": item.get("desc", ""),
            })
        out.append({
            "key": label,
            "label": label,
            "desc": desc,
            "steps": steps,
        })
    return out or None

'''

PIPELINE_START = "PIPELINE = [\n"
PIPELINE_END = 'STAGE_ORDER = [s["key"] for s in PIPELINE]\n'

NEW_PIPELINE = '''_RING_PIPELINE = _build_pipeline_from_rings()

PIPELINE = _RING_PIPELINE if _RING_PIPELINE else [
    {"key": "规划", "label": "规划", "desc": "（兜底）",
     "steps": [{"name": "规划复核", "norms": False, "blocks": ["产出"]}]},
    {"key": "写作", "label": "写作", "desc": "（兜底）",
     "steps": [{"name": "章纲", "norms": False, "blocks": ["产出"]},
               {"name": "正文", "norms": True, "blocks": ["产出"]}]},
    {"key": "去AI", "label": "去AI", "desc": "（兜底）",
     "steps": [{"name": "去AI润色", "norms": True, "blocks": ["产出"]}]},
    {"key": "审核", "label": "审核", "desc": "（兜底）",
     "steps": [{"name": "质检评审", "norms": True, "blocks": ["产出"]}]},
    {"key": "出厂", "label": "出厂", "desc": "（兜底）",
     "steps": [{"name": "出厂检查", "norms": True, "blocks": ["产出"]}]},
]

'''

A3 = '''def assign_block(state, stage_key, step_name, block_name, ai):
    step = _locate(state, stage_key, step_name)
    if block_name not in step["blocks"]:
        raise KeyError(f"子步 {step_name} 无大块: {block_name}")
    step["blocks"][block_name] = ai


def assign_role(state, stage_key, step_name, role, ai):
    if role not in ("reviewer", "adjuster"):
        raise ValueError("role 只能是 reviewer 或 adjuster")
    step = _locate(state, stage_key, step_name)
    step[role] = ai
'''

B3 = '''def assign_block(state, stage_key, step_name, block_name, ai):
    """执行者：ai 可为 str / list / None。"""
    step = _locate(state, stage_key, step_name)
    if block_name not in step["blocks"]:
        raise KeyError(f"子步 {step_name} 无大块: {block_name}")
    if isinstance(ai, list):
        ai = [x for x in ai if x] or None
    step["blocks"][block_name] = ai


def assign_role(state, stage_key, step_name, role, ai):
    """reviewer 可为 str / list / None；adjuster 为 str / None。"""
    if role not in ("reviewer", "adjuster"):
        raise ValueError("role 只能是 reviewer 或 adjuster")
    step = _locate(state, stage_key, step_name)
    if isinstance(ai, list):
        ai = [x for x in ai if x] or None
    step[role] = ai
'''


def main():
    print("=" * 60)
    print("patch_ui_rings — 让 UI 读 rings_items.json")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_build_pipeline_from_rings" in text and "_RING_PIPELINE" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_rings")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    if "def _load_rings_items" not in text:
        if A1 not in text:
            print("[失败] 改动1 锚点未找到")
            return
        text = text.replace(A1, B1, 1)
        print("✔ 改动1：已插入 _load_rings_items / _build_pipeline_from_rings")
    else:
        print("[跳过] 改动1 已存在")

    i = text.find(PIPELINE_START)
    j = text.find(PIPELINE_END)
    if i < 0 or j < 0:
        print("[失败] 改动2 锚点未找到（PIPELINE 定义）")
        return
    text = text[:i] + NEW_PIPELINE + text[j:]
    print("✔ 改动2：PIPELINE 已改为读 rings_items.json")

    if A3 not in text:
        print("[失败] 改动3 锚点未找到（assign_block/assign_role）")
        return
    text = text.replace(A3, B3, 1)
    print("✔ 改动3：assign_block / assign_role 支持 list")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()