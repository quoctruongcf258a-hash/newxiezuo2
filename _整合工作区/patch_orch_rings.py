# patch_orch_rings.py — 让 orchestrator.py 优先读 rings_items.json
#
# 改动 3 处：
#   1. 顶部加 STAGE_MAP + RINGS_JSON + _load_phases() 函数
#   2. run_program 里 phases = 那一行改为调 _load_phases
#   3. 幂等：已打过就跳过
import shutil
from pathlib import Path

SCRATCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
ORCH = SCRATCH / "orchestrator.py"

# ─── 改动 1：在 APPS_JSON 定义后插入 STAGE_MAP + RINGS_JSON + _load_phases ───
A1 = 'APPS_JSON = HERE / "apps.json"\n'
B1 = (
    'APPS_JSON = HERE / "apps.json"\n'
    'RINGS_JSON = HERE.parent.parent / "rules" / "rings_items.json"\n'
    '\n'
    '# 程序名 → rings_items.json 里的阶段键\n'
    'STAGE_MAP = {\n'
    '    "规划": "01_规划",\n'
    '    "写作": "02_写作",\n'
    '    "润色": "03_去AI",\n'
    '    "质检": "04_审核",\n'
    '}\n'
    '\n'
    '\n'
    'def _load_phases(cfg, program):\n'
    '    """优先从 rings_items.json 读该程序的环节清单；读不到则回退 cfg["phases"]。"""\n'
    '    if RINGS_JSON.exists():\n'
    '        try:\n'
    '            rings = json.loads(RINGS_JSON.read_text(encoding="utf-8"))\n'
    '        except Exception:\n'
    '            rings = None\n'
    '        if rings:\n'
    '            stage_key = STAGE_MAP.get(program)\n'
    '            if stage_key and stage_key in rings:\n'
    '                items = rings[stage_key].get("环节", [])\n'
    '                out = []\n'
    '                for item in items:\n'
    '                    out.append({\n'
    '                        "key": item.get("name") or item.get("code"),\n'
    '                        "code": item.get("code"),\n'
    '                        "mode": item.get("type") or "mesh",\n'
    '                        "stage": program,\n'
    '                        "supp": False,\n'
    '                        "desc": item.get("desc", ""),\n'
    '                    })\n'
    '                if out:\n'
    '                    print(f"[rings] 读入 {RINGS_JSON.name} 的 {stage_key}：{len(out)} 环")\n'
    '                    return out\n'
    '    return [p for p in cfg["phases"] if p["stage"] == program]\n'
    '\n'
)

# ─── 改动 2：run_program 里 phases = 那一行 ───
A2 = '    phases = [p for p in cfg["phases"] if p["stage"] == program]\n'
B2 = '    phases = _load_phases(cfg, program)\n'


def main():
    print("=" * 60)
    print("patch_orch_rings — 让 orchestrator 读 rings_items.json")
    print("=" * 60)

    if not ORCH.exists():
        print(f"[错误] 找不到 {ORCH}")
        return

    text = ORCH.read_text(encoding="utf-8")

    if "_load_phases" in text and "RINGS_JSON" in text:
        print("[跳过] 已打过补丁")
        return

    # 备份
    bak = ORCH.with_suffix(".py.bak_rings")
    if not bak.exists():
        shutil.copy(ORCH, bak)
        print(f"已备份：{bak.name}")

    # 改动 1
    if A1 not in text:
        print("[失败] 改动1 锚点未找到：APPS_JSON 定义")
        return
    if "RINGS_JSON" in text:
        print("[跳过] 改动1 已存在")
    else:
        text = text.replace(A1, B1, 1)
        print("✔ 改动1：已插入 STAGE_MAP / RINGS_JSON / _load_phases")

    # 改动 2
    if A2 not in text:
        print("[失败] 改动2 锚点未找到：run_program 里 phases = 那一行")
        print("       可能是缩进不同或已被改过")
        return
    if B2 in text:
        print("[跳过] 改动2 已存在")
    else:
        text = text.replace(A2, B2, 1)
        print("✔ 改动2：run_program 改为调 _load_phases")

    # 写回
    ORCH.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {ORCH}")
    print("\n下一步验证：")
    print("  cd 到 _scratch，跑 dry-run 看 01_规划 是否变成 33 环")


if __name__ == "__main__":
    main()