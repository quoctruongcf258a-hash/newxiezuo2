# patch_kw_v3.py — 关键词块只留内容词/动作词/红线（按行替换）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

NEW_BLOCK = (
    "    # _KEYWORDS：注入本环节关键词（从 apps.json 自动提取）\n"
    "    try:\n"
    "        _kw = keywords_for_phase(cfg, program, phase_cfg)\n"
    "        _kb = \"【本环节关键词（落笔时逐条对照）】\"\n"
    "        _has = False\n"
    "        if _kw[\"内容词\"]:\n"
    "            _kb += \"\\n  内容词：\" + \"、\".join(_kw[\"内容词\"][:10])\n"
    "            _has = True\n"
    "        if _kw[\"动作词\"]:\n"
    "            _kb += \"\\n  动作词：\" + \"、\".join(_kw[\"动作词\"][:10])\n"
    "            _has = True\n"
    "        if _kw[\"红线\"]:\n"
    "            _kb += \"\\n  红线：\" + \"、\".join(_kw[\"红线\"])\n"
    "            _has = True\n"
    "        if _has:\n"
    "            parts.append(_kb)\n"
    "    except Exception:\n"
    "        pass\n"
)

lines = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

start = None
for i, ln in enumerate(lines):
    if "# _KEYWORDS" in ln:
        start = i
        break

if start is None:
    print("[失败] 找不到 # _KEYWORDS 行")
    raise SystemExit(1)

end = None
for j in range(start, len(lines)):
    if lines[j].lstrip().startswith("pb = platform_block(cfg)"):
        end = j
        break

if end is None:
    print("[失败] 找不到 pb = platform_block(cfg) 行")
    raise SystemExit(1)

print(f"定位：_KEYWORDS 起始于第 {start+1} 行，pb=platform_block 在第 {end+1} 行")

bak = TARGET.with_suffix(".py.bak_kw3")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

new_lines = lines[:start] + [NEW_BLOCK] + lines[end:]
TARGET.write_text("".join(new_lines), encoding="utf-8")
print("✔ 已把关键词块改为只留 内容词/动作词/红线")
print(f"✔ 已写回 {TARGET}")