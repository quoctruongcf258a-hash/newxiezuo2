# fix_verify.py — 发送校验 + 运行校验
import shutil
from pathlib import Path

MIX = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
ORCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
changed = []

# ── 补丁 1：mix_send.py 加 check_running 函数 ──
text = MIX.read_text(encoding="utf-8")
if "def check_running" not in text:
    # 在 send() 定义前插入
    anchor = "def send(ai, text, retries=3, retry_delay=3):"
    if anchor in text:
        insert = '''def check_running(ai):
    """检查 AI 是否正在生成（窗口有「停止」按钮）。
    返回: 'running' / 'idle' / 'err: xxx'"""
    info = _lookup(ai)
    if not info or not info[0]:
        return "err: 无端口"
    port, kw = info
    try:
        t = CDPTab(port, kw)
        r = t.js("""
        (() => {
            const btns = [...document.querySelectorAll('button, [role="button"]')];
            for (const b of btns) {
                const a = (b.getAttribute('aria-label')||'').trim();
                if (a === '停止' || a === 'Stop' || a === 'stop' || a === '停止生成') {
                    const rr = b.getBoundingClientRect();
                    if (rr.width > 0 && rr.height > 0) return 'running';
                }
            }
            return 'idle';
        })()
        """)
        return r if r else "idle"
    except Exception as e:
        return f"err: {e}"


'''
        text = text.replace(anchor, insert + anchor, 1)
        MIX.write_text(text, encoding="utf-8")
        changed.append("check_running 函数")
    else:
        print("✗ 找不到 send 函数锚点")

# ── 补丁 2：mix_send.py 里 send() 判断是否真发送 ──
text = MIX.read_text(encoding="utf-8")
OLD = '''                if r in ("no-input", None):
                    raise Exception(f"CDP 找不到可用输入框（{r}）")
                if _attempt > 0:
                    print(f"[CDP 重试] {ai} 第 {_attempt+1}/{retries} 次成功")
                return f"✅ {ai}: CDP {r}"'''
NEW = '''                if r in ("no-input", None):
                    raise Exception(f"CDP 找不到可用输入框（{r}）")
                # 严格判断：输入框还有内容说明没发出去
                if isinstance(r, str) and r.startswith("剩余="):
                    raise Exception(f"发送未生效：{r}")
                if _attempt > 0:
                    print(f"[CDP 重试] {ai} 第 {_attempt+1}/{retries} 次成功")
                return f"✅ {ai}: CDP {r}"'''
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    MIX.write_text(text, encoding="utf-8")
    changed.append("send() 严格判断")
elif "发送未生效" in text:
    print("send() 已改过")

# ── 补丁 3：orchestrator.py run_task 里加校验 ──
otext = ORCH.read_text(encoding="utf-8")
OLD_R = '''            r = _cdp_send(label, prompt)
            print(f"[CDP] 返回：{r}")
            # 判断是否真发送成功：mix_send 返回值以 ✅ 开头为成功
            _rs = str(r or "")
            if _rs.lstrip().startswith("✅"):
                return True
            print("[CDP] 返回非成功标记，判定为失败")
            return False
        except Exception as e:                 # noqa: BLE001
            print(f"[CDP 失败] {e}，回退 windows_use")
'''

NEW_R = '''            r = _cdp_send(label, prompt)
            print(f"[CDP] 返回：{r}")
            # 判断是否真发送成功：mix_send 返回值以 ✅ 开头为成功
            _rs = str(r or "")
            if _rs.lstrip().startswith("✅"):
                # 发送后运行校验（3 秒后查「停止」按钮）
                try:
                    time.sleep(3)
                    from mix_send import check_running as _chk
                    _st = _chk(label)
                    if _st == "running":
                        print(f"[校验] ✓ {label} 正在运行")
                    elif _st == "idle":
                        print(f"[校验] ⚠ {label} 未检测到运行（可能已回复完）")
                    else:
                        print(f"[校验] ⚠ {label} 状态：{_st}")
                except Exception as _ve:
                    print(f"[校验] 异常：{_ve}")
                return True
            print("[CDP] 返回非成功标记，判定为失败")
            return False
        except Exception as e:                 # noqa: BLE001
            print(f"[CDP 失败] {e}，回退 windows_use")
'''
if OLD_R in otext:
    otext = otext.replace(OLD_R, NEW_R, 1)
    ORCH.write_text(otext, encoding="utf-8")
    changed.append("run_task 运行校验")
elif "运行校验（3 秒后查" in otext:
    print("run_task 已改过")

# ── 补丁 4：run_mesh_phase writers 并发段汇总输出 ──
otext = ORCH.read_text(encoding="utf-8")
OLD_S = '''        else:
            # 单写手或 dry-run：串行
            for w in writers:
                v = do_produce(agent, sess, w, program, phase_cfg, cid, clabel,
                               input_text, out_dir, dry, extra_note=extra_issues,
                               ai_assist=assist)
                if dry or (v.exists() and v.stat().st_size > 0):
                    versions.append(v)
'''
NEW_S = '''        else:
            # 单写手或 dry-run：串行
            for w in writers:
                v = do_produce(agent, sess, w, program, phase_cfg, cid, clabel,
                               input_text, out_dir, dry, extra_note=extra_issues,
                               ai_assist=assist)
                if dry or (v.exists() and v.stat().st_size > 0):
                    versions.append(v)

        # 汇总产出校验
        _out_keys = {v.stem.split("__")[-1] for v in versions if v}
        _expect_keys = {w["key"] for w in writers}
        _missing = _expect_keys - _out_keys
        print(f"  [产出校验] 期望 {len(_expect_keys)} 个，落盘 {len(_out_keys)} 个")
        if _missing:
            print(f"  [产出校验] ⚠ 未落盘：{_missing}")
'''
if OLD_S in otext:
    otext = otext.replace(OLD_S, NEW_S, 1)
    ORCH.write_text(otext, encoding="utf-8")
    changed.append("产出校验汇总")
elif "产出校验] 期望" in otext:
    print("产出校验已加")

if changed:
    for f, suf in [(MIX, ".py.bak_verify"), (ORCH, ".py.bak_verify")]:
        bak = f.with_suffix(suf)
        if not bak.exists():
            shutil.copy(f, bak)
            print(f"已备份：{bak.name}")
    print()
    for c in changed:
        print(f"✔ {c}")
else:
    print("没有改动")