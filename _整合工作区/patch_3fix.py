import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_3fix")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ══════════════════════════════════════════════════════════════
# 修 1：_do_produce_batch 的 verify_fn 用目录隔离
# ══════════════════════════════════════════════════════════════
OLD1 = '''    def verify_fn(ai_key_override=None):
        # 因为兜底时 ai_key 会变，需要动态计算路径
        _ai = ai_key_override or primary_key
        missing = 0
        for item_key, _ in expected:
            safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
            p = _versions_dir / f"{_ai}__{safe}.md"
            if not (p.exists() and p.stat().st_size >= 100):
                missing += 1
        total = len(expected)
        ok = (missing == 0)
        return ok, f"{total - missing}/{total}"'''

NEW1 = '''    _is_single = (len(expected) == 1)

    def verify_fn(ai_key_override=None):
        # 目录隔离：versions/<ai>/<item>.md
        _ai = ai_key_override or primary_key
        _ai_dir = _versions_dir / _ai
        missing = 0
        total_size = 0
        for item_key, _ in expected:
            if _is_single:
                # 生产者：文件名 = phase_name.md
                p = _ai_dir / f"{item_key}.md"
            else:
                safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                p = _ai_dir / f"{safe}.md"
            if p.exists() and p.stat().st_size >= 200:
                total_size += p.stat().st_size
            else:
                missing += 1
        total = len(expected)
        ok = (missing == 0)
        return ok, f"{total - missing}/{total}（{total_size}B）"'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 修1：verify_fn 用目录隔离 + 非空校验")
    changed += 1
else:
    print("[FAIL] 修1 找不到锚点")

# ══════════════════════════════════════════════════════════════
# 修 2：do_review 未抓到回复返回 None
# ══════════════════════════════════════════════════════════════
OLD2 = '''            if _txt:
                import re as _re
                # 从回复里抠 JSON（第一个 { 到最后一个 }）
                _m = _re.search(r"\\{.*\\}", _txt, _re.S)
                _payload = _m.group(0) if _m else _txt
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(_payload, encoding="utf-8")
                print(f"[盲审] 已抓取并落盘：{out.name}（{len(_payload)} 字，baseline {len(_baseline)} 字）")
            else:
                print(f"[盲审] 未抓到新回复：{app['key']}（baseline {len(_baseline)} 字）")
        except Exception as _e:
            print(f"[盲审] capture 失败：{_e}")
    return out'''

NEW2 = '''            if _txt:
                import re as _re
                _m = _re.search(r"\\{.*\\}", _txt, _re.S)
                _payload = _m.group(0) if _m else _txt
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(_payload, encoding="utf-8")
                print(f"[盲审] ✅ 已抓取并落盘：{out.name}（{len(_payload)} 字）")
                return out   # ✅ 成功才返回
            else:
                print(f"[盲审] ❌ 未抓到新回复：{app['key']}（baseline {len(_baseline)} 字）")
                return None   # ❌ 失败返回 None，触发重试/兜底
        except Exception as _e:
            print(f"[盲审] ❌ capture 失败：{_e}")
            return None
    return None'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 修2：do_review 未抓到返回 None")
    changed += 1
else:
    print("[FAIL] 修2 找不到锚点")

# ══════════════════════════════════════════════════════════════
# 修 3：加清理函数 + 在 run_mesh_phase 开头调用
# ══════════════════════════════════════════════════════════════
FUNC = r'''


def _clean_old_named_files(out_dir):
    """清理 versions/ 根目录下旧命名（带 __ 分隔符）的 md 文件。
    保留目录隔离后的 versions/<ai>/ 结构。
    """
    versions_dir = Path(out_dir) / "versions"
    if not versions_dir.exists():
        return 0
    cnt = 0
    for f in versions_dir.glob("*.md"):
        if f.is_file() and "__" in f.name:
            try:
                f.unlink()
                cnt += 1
                print(f"   [清理] 删旧命名：{f.name}")
            except Exception as e:
                print(f"   [清理] 失败：{f.name}（{e}）")
    if cnt:
        print(f"   [清理] 共删 {cnt} 个旧命名文件")
    return cnt
'''

# 插入函数（放在 _do_produce_batch 之前）
anchor = "def _do_produce_batch("
if anchor in text and "_clean_old_named_files" not in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 修3a：插入 _clean_old_named_files")

# 在 _run_batch_mesh 开头调用
OLD3 = '''    versions_dir = Path(out_dir) / "versions"

    # 阶段1：产出'''
NEW3 = '''    versions_dir = Path(out_dir) / "versions"

    # ── 清理旧命名文件（防残留干扰）──
    _clean_old_named_files(out_dir)

    # 阶段1：产出'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 修3b：_run_batch_mesh 开头调清理")
    changed += 1
else:
    print("[WARN] 修3b 找不到锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 共修改 {changed} 处")
