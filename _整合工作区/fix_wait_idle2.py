# fix_wait_idle2.py — 用「忙特征」精准等空闲
import shutil
from pathlib import Path

MIX = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = MIX.read_text(encoding="utf-8")

# 替换 wait_idle 的实现
import re
pat = re.compile(r"def wait_idle\(ai, timeout=600, poll=5\):.*?\n    return False\n", re.S)

NEW_IDLE = '''def _is_busy(ai):
    """判断 AI 是否正在生成 / 有排队任务。返回 True/False。"""
    info = _lookup(ai)
    if not info or not info[0]:
        return False
    port, kw = info
    try:
        tab = CDPTab(port, kw)
        key = ai.lower()
        if key == "quest":
            # QUEST：有 send-queue-* 类按钮 = 忙
            return bool(tab.js("""
            (() => !!document.querySelector('[class*="send-queue-"]'))()
            """))
        if key == "workbuddy":
            # WorkBuddy：查「停止」按钮（生成时出现）或发送按钮 disabled
            return bool(tab.js("""
            (() => {
                for (const b of document.querySelectorAll('button')) {
                    const a = (b.getAttribute('aria-label')||'').trim();
                    const r = b.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    if (a === '停止' || a === 'Stop') return true;
                }
                return false;
            })()
            """))
        if key == "doubao":
            # Doubao：查「停止」按钮
            return bool(tab.js("""
            (() => {
                const txt = (document.body.innerText || '');
                if (/停止生成|停止回答/.test(txt)) return true;
                for (const b of document.querySelectorAll('button')) {
                    const a = (b.getAttribute('aria-label')||'').trim();
                    if (a === '停止' || a === 'Stop' || a === '停止生成') {
                        const r = b.getBoundingClientRect();
                        if (r.width > 0 && r.height > 0) return true;
                    }
                }
                return false;
            })()
            """))
        if key == "gemini":
            # gemini：查「停止」按钮
            return bool(tab.js("""
            (() => {
                for (const b of document.querySelectorAll('button, [role="button"]')) {
                    const a = (b.getAttribute('aria-label')||'').trim().toLowerCase();
                    const r = b.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    if (a === 'stop' || a === 'stop generating' || a === 'cancel') return true;
                }
                return false;
            })()
            """))
        # 通用：查输入框空 + 发送按钮状态
        return False
    except Exception:
        return False


def wait_idle(ai, timeout=600, poll=5):
    """等 AI 空闲（无排队任务 + 无生成中）。超时返回 False。"""
    import time as _t
    t0 = _t.time()
    while _t.time() - t0 < timeout:
        if not _is_busy(ai):
            return True
        _t.sleep(poll)
    return False


'''

if "def _is_busy(ai):" in text:
    print("已改过")
elif pat.search(text):
    text = pat.sub(NEW_IDLE, text, count=1)
    bak = MIX.with_suffix(".py.bak_idle2")
    if not bak.exists():
        shutil.copy(MIX, bak)
        print(f"已备份：{bak.name}")
    MIX.write_text(text, encoding="utf-8")
    print("✔ wait_idle + _is_busy 已替换")
else:
    print("✗ 找不到 wait_idle 定义")