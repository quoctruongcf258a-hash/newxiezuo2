# fix_capture.py — capture 放开 electron 类型检查
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")
changed = []

# 补丁 1a：capture
OLD1 = '''def capture(ai):
    """抓取网页端 AI 的回复文本（CDP）；非网页端或失败返回空串。"""
    if _type_of(ai) != "web":
        return ""
    info = _lookup(ai)'''
NEW1 = '''def capture(ai):
    """抓取 AI 的回复文本（CDP，含 electron）；失败返回空串。"""
    info = _lookup(ai)'''
if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    changed.append("capture")

# 补丁 1b：capture_with_meta
OLD2 = '''    """同 capture，但额外返回结构化信息：{"text", "n", "bodyLen"}。
    n 为命中的助手消息气泡数；n==0 表示只抓到整页回退文本（未真正回复），供调用方判定真伪。"""
    if _type_of(ai) != "web":
        return {"text": "", "n": 0, "bodyLen": 0}
    info = _lookup(ai)'''
NEW2 = '''    """同 capture，但额外返回结构化信息：{"text", "n", "bodyLen"}。
    n 为命中的助手消息气泡数；n==0 表示只抓到整页回退文本（未真正回复），供调用方判定真伪。"""
    info = _lookup(ai)'''
if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    changed.append("capture_with_meta")

if changed:
    bak = TARGET.with_suffix(".py.bak_capture")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    for c in changed:
        print(f"✔ {c} 已放开 electron")
else:
    print("没有改动（可能已改过）")