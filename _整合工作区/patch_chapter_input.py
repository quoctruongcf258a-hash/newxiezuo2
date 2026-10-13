import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# ── 补丁 A：新增 _read_upstream_for_chapter 函数 ──
FUNC = r'''


def _read_upstream_for_chapter(program, phase_cfg, chapter_no, out_dir):
    """为第 N 章读专属上游文件内容，返回拼好的字符串（可能为空）。
    写作阶段专用：W0 读 P18 章纲，W1~W4 读同程序前序环节的同章产出。
    """
    parts = []
    name = phase_cfg.get("name") or phase_cfg.get("key") or ""
    od = Path(out_dir)

    WRITE_ORDER = ["W0_细纲分析", "W1_章前对齐卡", "W2_分布", "W3_正文", "W4_章内节奏自检"]

    if program == "写作" and name in WRITE_ORDER:
        write_root = od.parent          # .../02_写作/
        cur_idx = WRITE_ORDER.index(name)

        # W0 读 01_规划/前30章落地章纲/versions/*__章N.md
        if cur_idx == 0:
            proj_root = write_root.parent
            p18_dir = proj_root / "01_规划" / "前30章落地章纲" / "versions"
            if p18_dir.exists():
                for f in sorted(p18_dir.glob(f"*__章{chapter_no}.md")):
                    try:
                        c = f.read_text(encoding="utf-8", errors="ignore")
                        if len(c) > 4000:
                            c = c[:4000] + f"\n…（已截断，全文 {len(c)} 字）"
                        parts.append(f"【上游：前30章落地章纲 第{chapter_no}章（{f.name}）】\n{c}")
                    except Exception:
                        pass

        # W1~W4 读同程序前序环节的同章产出
        for prev_name in WRITE_ORDER[:cur_idx]:
            prev_dir = write_root / prev_name / "versions"
            if not prev_dir.exists():
                continue
            for f in sorted(prev_dir.glob(f"*__章{chapter_no}.md")):
                try:
                    c = f.read_text(encoding="utf-8", errors="ignore")
                    if len(c) > 4000:
                        c = c[:4000] + f"\n…（已截断，全文 {len(c)} 字）"
                    parts.append(f"【上游：{prev_name} 第{chapter_no}章（{f.name}）】\n{c}")
                except Exception:
                    pass

    return "\n\n".join(parts)
'''

anchor = '\nif __name__ == "__main__":'
i_main = text.find(anchor)
if i_main < 0:
    print("[FAIL] 找不到 __main__ 锚点")
elif "_read_upstream_for_chapter" in text:
    print("[SKIP] A：函数已存在")
else:
    before = text[:i_main].rstrip()
    after = text[i_main:]
    text = before + "\n\n\n" + FUNC.strip() + "\n\n" + after.lstrip("\n")
    print("[OK] A：插入 _read_upstream_for_chapter")

# ── 补丁 B：_do_produce_split 循环里追加按章上游 ──
OLD_B = '''        _item_note = (_base_note + "\\n\\n【本次任务（只做这一项，不要处理其他项）】\\n"
                       + _json.dumps(item, ensure_ascii=False, indent=2))
        _label = f"{program} › {_phase_name} › {_key}"'''

NEW_B = '''        _item_note = (_base_note + "\\n\\n【本次任务（只做这一项，不要处理其他项）】\\n"
                       + _json.dumps(item, ensure_ascii=False, indent=2))
        _label = f"{program} › {_phase_name} › {_key}"

        # 按章追加专属上游（写作阶段：W0 读 P18 章纲；W1~W4 读前序环节同章产出）
        _ch_no = item.get("start") or item.get("end") or item.get("章号") or 0
        try:
            _ch_no = int(_ch_no)
        except Exception:
            _ch_no = 0
        if _ch_no:
            _extra_input = _read_upstream_for_chapter(program, phase_cfg, _ch_no, out_dir)
            if _extra_input:
                _item_input = input_text + "\\n\\n" + _extra_input
                print(f"   [{_key}] 追加按章上游：{len(_extra_input)} 字")
            else:
                _item_input = input_text
        else:
            _item_input = input_text'''

if OLD_B in text:
    text = text.replace(OLD_B, NEW_B, 1)
    print("[OK] B：_do_produce_split 追加按章上游变量")
else:
    print("[FAIL] B 找不到 _item_note 锚点")

# ── 补丁 C：把 build_produce_task 里的 input_text 换成 _item_input ──
OLD_C = '''        if ai_assist:
            _task = tasks_mod.build_scaffold_task(app, _tpl, input_text, str(_out), _label)
        else:
            _task = tasks_mod.build_produce_task(
                app, _tpl, input_text, str(_out),
                _label, f"{chunk_label} · {_key}", _item_note
            )'''

NEW_C = '''        if ai_assist:
            _task = tasks_mod.build_scaffold_task(app, _tpl, _item_input, str(_out), _label)
        else:
            _task = tasks_mod.build_produce_task(
                app, _tpl, _item_input, str(_out),
                _label, f"{chunk_label} · {_key}", _item_note
            )'''

if OLD_C in text:
    text = text.replace(OLD_C, NEW_C, 1)
    print("[OK] C：build_produce_task 用 _item_input")
else:
    print("[WARN] C 找不到 build_produce_task 锚点（可能只改了 scaffold 分支）")
    # 尝试只替换 input_text
    OLD_C2 = 'tasks_mod.build_produce_task(\n                app, _tpl, input_text, str(_out),'
    NEW_C2 = 'tasks_mod.build_produce_task(\n                app, _tpl, _item_input, str(_out),'
    if OLD_C2 in text:
        text = text.replace(OLD_C2, NEW_C2, 1)
        print("[OK] C2：用更宽的锚点替换成功")

# ── 写回 ──
bak = TARGET.with_suffix(".py.bak_chapter_input")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回：{TARGET.name}")
