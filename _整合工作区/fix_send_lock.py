# fix_send_lock.py — 加全局发送锁，解决剪贴板竞争
import shutil
from pathlib import Path

MIX = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = MIX.read_text(encoding="utf-8")

# 1) 加 import threading + 全局锁
if "_SEND_LOCK" not in text:
    if "import threading" not in text:
        text = text.replace("import json, urllib.request, websocket, time, os, sys",
                            "import json, urllib.request, websocket, time, os, sys, threading",
                            1)
    # 在 _LAST_SENT 后加锁定义
    anchor = "_LAST_SENT = {}"
    if anchor in text:
        text = text.replace(anchor,
                            anchor + "\n\n# 发送锁：CDP 发送依赖系统剪贴板，并发会互相覆盖\n_SEND_LOCK = threading.Lock()",
                            1)
        print("✔ 加了 _SEND_LOCK")

# 2) 修改 send 函数签名，用锁包起来
OLD = '''def send(ai, text, retries=3, retry_delay=3):
    """发送。CDP 失败会重试 retries 次（每次 retry_delay 秒）；仍失败才降级 pyautogui。"""
    _LAST_SENT[ai] = text'''
NEW = '''def send(ai, text, retries=3, retry_delay=3):
    """发送。CDP 失败会重试 retries 次（每次 retry_delay 秒）；仍失败才降级 pyautogui。

    注意：内部用 _SEND_LOCK 串行化——CDP 发送依赖系统剪贴板，并发会互相覆盖。
    """
    with _SEND_LOCK:
        return _send_locked(ai, text, retries, retry_delay)


def _send_locked(ai, text, retries=3, retry_delay=3):
    """实际发送逻辑（调用者需持 _SEND_LOCK）。"""
    _LAST_SENT[ai] = text'''
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("✔ send() 已改成加锁版本")
elif "_send_locked" in text:
    print("send() 已改过")
else:
    print("✗ 找不到 send 函数")

MIX.write_text(text, encoding="utf-8")
print("已保存")