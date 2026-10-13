# fix_board_call.py — 记分榜调用加 try-except，函数不存在就跳过
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    # 赛马记分榜：登记参与 + 解析拼接者的采纳标记
    if not dry:
        for w in {v.stem.split("__")[-1] for v in versions}:
            board_mod.note_participation(program, phase_cfg["key"], w)
        pairs = []
        for cid, _cl, _s in chunks:
            mt = read_text(Path(out_dir) / "merged" / f"{cid}.md")
            for ck, wk in board_mod.parse_adopt_markers(mt):
                pairs.append((ck or cid, wk))
        if pairs:
            board_mod.record_adoptions(program, chapter, phase_cfg["key"], pairs)
            print(f"📊 记分榜：本环节采纳 → "
                  + "、".join(f"{wk}×{sum(1 for _, w2 in pairs if w2 == wk)}"
                              for wk in {w2 for _, w2 in pairs}))
'''

NEW = '''    # 赛马记分榜：登记参与 + 解析拼接者的采纳标记
    # （可选功能；scoreboard 缺函数时跳过，不影响主流程）
    if not dry:
        try:
            if hasattr(board_mod, "note_participation"):
                for w in {v.stem.split("__")[-1] for v in versions}:
                    board_mod.note_participation(program, phase_cfg["key"], w)
            if hasattr(board_mod, "parse_adopt_markers") and hasattr(board_mod, "record_adoptions"):
                pairs = []
                for cid, _cl, _s in chunks:
                    mt = read_text(Path(out_dir) / "merged" / f"{cid}.md")
                    for ck, wk in board_mod.parse_adopt_markers(mt):
                        pairs.append((ck or cid, wk))
                if pairs:
                    board_mod.record_adoptions(program, chapter, phase_cfg["key"], pairs)
                    print(f"📊 记分榜：本环节采纳 → "
                          + "、".join(f"{wk}×{sum(1 for _, w2 in pairs if w2 == wk)}"
                                      for wk in {w2 for _, w2 in pairs}))
        except Exception as _e:
            print(f"[记分榜] 跳过（{_e}）")
'''

if "记分榜] 跳过" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("赛马记分榜")
    if i >= 0:
        print(repr(text[i-50:i+200]))
else:
    bak = TARGET.with_suffix(".py.bak_boardcall")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 记分榜调用已加保护")