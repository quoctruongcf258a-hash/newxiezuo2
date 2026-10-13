# fix_cdp_retry.py — send() 加 CDP 重试（3 次，每次 3 秒）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''def send(ai, text):
    _LAST_SENT[ai] = text
    if ai in CDP_APPS:
        try:
            r = send_via_cdp(ai, text)
            if r in ("no-input", None):
                raise Exception(f"CDP 找不到可用输入框（{r}）")
            return f"✅ {ai}: CDP {r}"
        except Exception as e:
            msg = f"⚠ {ai}: CDP 失败 {e}"
            # CDP 取不到输入（如概览区弹出、浮层遮挡）时，降级到 pyautogui 再试一次
            if ai in PYA_APPS:
                try:
                    r2 = send_via_pyautogui(ai, text)
                    if _pya_ok(r2):
                        return f"✅ {ai}: {r2}（CDP 失败已兜底：{e}）"
                    return f"{msg}；pyautogui 兜底失败：{r2}"
                except Exception as e2:
                    return f"{msg}；pyautogui 兜底也失败：{e2}"
            return msg
'''

NEW = '''def send(ai, text, retries=3, retry_delay=3):
    """发送。CDP 失败会重试 retries 次（每次 retry_delay 秒）；仍失败才降级 pyautogui。"""
    _LAST_SENT[ai] = text
    if ai in CDP_APPS:
        last_err = None
        for _attempt in range(retries):
            try:
                r = send_via_cdp(ai, text)
                if r in ("no-input", None):
                    raise Exception(f"CDP 找不到可用输入框（{r}）")
                if _attempt > 0:
                    print(f"[CDP 重试] {ai} 第 {_attempt+1}/{retries} 次成功")
                return f"✅ {ai}: CDP {r}"
            except Exception as e:
                last_err = e
                if _attempt < retries - 1:
                    print(f"[CDP 重试] {ai} 第 {_attempt+1}/{retries} 次失败：{e}，{retry_delay}s 后重试")
                    time.sleep(retry_delay)
                    continue
                break
        msg = f"⚠ {ai}: CDP 失败 {last_err}（已重试 {retries} 次）"
        # 全部重试失败后，才降级 pyautogui 兜底
        if ai in PYA_APPS:
            try:
                r2 = send_via_pyautogui(ai, text)
                if _pya_ok(r2):
                    return f"✅ {ai}: {r2}（CDP 重试失败已兜底：{last_err}）"
                return f"{msg}；pyautogui 兜底失败：{r2}"
            except Exception as e2:
                return f"{msg}；pyautogui 兜底也失败：{e2}"
        return msg
'''

if "CDP 失败会重试 retries 次" in text:
    print("已改过")
elif OLD not in text:
    print("找不到 send 函数锚点")
    i = text.find("def send(ai, text):")
    if i >= 0:
        print(text[i:i+800])
else:
    bak = TARGET.with_suffix(".py.bak_cdpretry")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 补丁1：send() 已加 CDP 重试（3 次，每次 3 秒）")