"""core/delivery.py
薄封装 windows-use/mix_send.send，统一「发任务 -> (尽力)收答复」。
- dry_run=True：不驱动任何窗口，返回模拟产出，便于无窗口环境验证流水线。
- dry_run=False：调用 mix_send 真实发送；回复抓取走 core/cdp_reply 尽力而为，
  失败/缺依赖则安全回退到模拟文本（标注来源），绝不抛异常中断。
"""
import sys
import os
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../multi-ai-pipeline
_WIN_USE = os.path.join(_ROOT, "windows-use")

if _WIN_USE not in sys.path:
    sys.path.insert(0, _WIN_USE)

try:
    from mix_send import send as _mix_send
    _HAS_MIX = True
except Exception:
    _HAS_MIX = False


def _sim_text(ai: str, prompt: str) -> str:
    """确定性模拟产出，使 dry-run 全流程可演示。"""
    n = 120 + (hash(ai) % 240)
    return (
        f"【{ai} 模拟产出】针对目标「{prompt[:40]}…」的示例正文段落：\n"
        f"夜色像浸了墨的绸，贴着窗沿往下淌。他按住门把，听见身后一声极轻的、"
        f"仿佛来自记忆深处的叹息——那声音他认得，却想不起属于谁。风把走廊尽头的"
        f"灯吹得忽明忽暗，影子在墙上拉成细长的一条，像有人在缓慢地、耐心地丈量"
        f"他与真相之间的距离。（本段为 dry-run 占位文本，长度约 {n} 字）"
    )


def dispatch(ai: str, prompt: str, dry_run: bool = False, wait: int = 6) -> dict:
    """发送一个任务给某 AI，返回 {status, text, source, raw?}。"""
    if dry_run or not _HAS_MIX:
        return {"status": "ok", "text": _sim_text(ai, prompt), "source": "sim"}

    raw = _mix_send(ai, prompt)
    ok = isinstance(raw, str) and raw.startswith("✅")
    if not ok:
        # 发送失败：回退模拟，但保留原始错误便于排查
        return {"status": "send_fail", "text": _sim_text(ai, prompt),
                "source": "sim", "raw": raw}

    # 发送成功：尽力抓取回复
    try:
        from cdp_reply import grab_last_reply
        reply = grab_last_reply(ai, wait=wait)
    except Exception:
        reply = None
    if reply:
        return {"status": "ok", "text": reply, "source": "real", "raw": raw}
    # 抓取不到：安全回退（明确标注），保证流水线不中断
    return {"status": "ok", "text": _sim_text(ai, "(真实窗口已发送，但未能自动取回回复)"),
            "source": "real_unfetched", "raw": raw}


def batch_dispatch(items: list, dry_run: bool = False, wait: int = 6) -> dict:
    """items: [(ai, prompt), ...] -> {ai: dispatch_result}。"""
    out = {}
    for ai, prompt in items:
        out[ai] = dispatch(ai, prompt, dry_run=dry_run, wait=wait)
    return out


def mix_available() -> bool:
    return _HAS_MIX
