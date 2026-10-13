# install_busy_check.py — 在 mix_send.py 里安装「忙闲检测」
import shutil
from pathlib import Path

MIX = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = MIX.read_text(encoding="utf-8")

MODULE = '''

# ═══════════ 忙闲检测模块 ═══════════
def is_ai_busy(ai):
    """检测 AI 是否正在生成/有排队任务。True=忙，False=空闲。"""
    info = _lookup(ai)
    if not info or not info[0]:
        return False
    port, kw = info
    try:
        tab = CDPTab(port, kw)
        return bool(tab.js("""
        (() => {
            // 1. 找「停止」按钮（几乎所有 AI 生成时都显示）
            for (const b of document.querySelectorAll('button, [role="button"]')) {
                const r = b.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) continue;
                const a = (b.getAttribute('aria-label')||'').trim();
                const t = (b.getAttribute('title')||'').trim();
                const txt = (b.textContent||'').trim();
                const al = a.toLowerCase();
                const tl = t.toLowerCase();
                if (al === 'stop' || al === 'stop generating' || al === 'cancel' ||
                    al === '\\u505c\\u6b62' || al === '\\u505c\\u6b62\\u751f\\u6210' ||
                    tl === 'stop' || tl === '\\u505c\\u6b62' ||
                    txt === '\\u505c\\u6b62' || txt === 'Stop') {
                    return true;
                }
            }
            // 2. QUEST：有 send-queue-* 类 = 有排队任务
            if (document.querySelector('[class*="send-queue-"]')) return true;
            // 3. 通用：页面含「生成中/思考中/正在」等文案
            const body = document.body.innerText || '';
            if (/\\u751f\\u6210\\u4e2d|\\u601d\\u8003\\u4e2d|\\u6b63\\u5728\\u601d\\u8003|\\u6b63\\u5728\\u751f\\u6210|Generating|Thinking/.test(body)) {
                return true;
            }
            return false;
        })()
        """))
    except Exception:
        return False


def wait_idle(ai, timeout=300, poll=5):
    """等 AI 空闲（无停止按钮 + 无排队 + 无生成中）。超时返回 False。"""
    import time as _t
    t0 = _t.time()
    while _t.time() - t0 < timeout:
        if not is_ai_busy(ai):
            return True
        _t.sleep(poll)
    return False
# ════════════════════════════════════

'''

# 检查是否已安装
if "def is_ai_busy" in text:
    print("✔ 已安装过，跳过")
else:
    # 在最后一个函数定义后插入（在 `if __name__ == "__main__"` 前）
    marker = 'if __name__ == "__main__":'
    if marker in text:
        text = text.replace(marker, MODULE + marker, 1)
        bak = MIX.with_suffix(".py.bak_busycheck")
        if not bak.exists():
            shutil.copy(MIX, bak)
            print(f"已备份：{bak.name}")
        MIX.write_text(text, encoding="utf-8")
        print("✔ 已安装 is_ai_busy + wait_idle")
    else:
        # 追加到文件末尾
        text += MODULE
        bak = MIX.with_suffix(".py.bak_busycheck")
        if not bak.exists():
            shutil.copy(MIX, bak)
            print(f"已备份：{bak.name}")
        MIX.write_text(text, encoding="utf-8")
        print("✔ 已追加到文件末尾")