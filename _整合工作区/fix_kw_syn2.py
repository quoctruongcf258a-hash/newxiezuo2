# fix_kw_syn2.py — 用行定位，替换 keywords_for_phase 里规划段
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

lines = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

# 找 def keywords_for_phase
i_func = None
for i, ln in enumerate(lines):
    if ln.startswith("def keywords_for_phase"):
        i_func = i
        break
if i_func is None:
    print("找不到 keywords_for_phase")
    raise SystemExit(1)

# 找函数体内第 1 个 if program == "规划"
i_plan = None
for i in range(i_func, len(lines)):
    if lines[i].strip() == 'if program == "规划":':
        i_plan = i
        break

# 找下一个 if program == "写作"
i_write = None
for i in range(i_plan + 1, len(lines)):
    if lines[i].strip() == 'if program == "写作":':
        i_write = i
        break

if i_plan is None or i_write is None:
    print(f"定位失败 i_plan={i_plan} i_write={i_write}")
    raise SystemExit(1)

print(f"规划段：第 {i_plan+1} 行，写作段：第 {i_write+1} 行")
print("旧代码：")
print("".join(lines[i_plan:i_write]))

NEW = '''    if program == "规划":
        # 内容词只取 desc 里 → 前面的部分（→ 后面是动作）
        _desc = (phase_cfg.get("desc") or "").strip()
        if _desc:
            _head = _desc
            for _sep in ("→", "->", "=>"):
                if _sep in _head:
                    _head = _head.split(_sep)[0]
                    break
            for _part in re.split(r"[+/、，,；;]+", _head):
                _p = _part.strip()
                if _p and len(_p) <= 12 and not _p.startswith("输出"):
                    out["内容词"].append(_p)

'''

bak = TARGET.with_suffix(".py.bak_kwsyn2")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

new_lines = lines[:i_plan] + [NEW] + lines[i_write:]
TARGET.write_text("".join(new_lines), encoding="utf-8")
print("✔ 已写回")