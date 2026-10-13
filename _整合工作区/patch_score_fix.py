import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_score_fix")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

# 在 _SCORE_JS 里的可见性过滤后，追加屏幕外过滤 + CodeMirror 重罚
OLD = """    if (r.width <= 0 || r.height <= 0) continue;
    if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0' || el.offsetParent === null) continue;"""

NEW = """    if (r.width <= 0 || r.height <= 0) continue;
    if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0' || el.offsetParent === null) continue;
    // _VIEWPORT_FILTER：屏幕外的元素直接跳过（CodeMirror 等藏在 -3000+ 位置）
    if (r.bottom < 0 || r.top > window.innerHeight) continue;
    if (r.right < 0 || r.left > window.innerWidth) continue;"""

if OLD in text and "_VIEWPORT_FILTER" not in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 已加屏幕外过滤")
else:
    print("[SKIP] 屏幕外过滤：已存在或没匹配到")

# CodeMirror class 重罚：在现有文件编辑器惩罚那行后面追加
OLD2 = """    if (/root-editable|file-edit|code-editor|monaco|editor-container/i.test(
            (el.className || '').toString())) score -= 100000000;"""

NEW2 = """    if (/root-editable|file-edit|code-editor|monaco|editor-container/i.test(
            (el.className || '').toString())) score -= 100000000;
    // _CODEMIRROR_PENALTY：CodeMirror 编辑器的 class 也重罚（cm-content/cm-editor 等）
    if (/\\bcm-(content|editor|scroll|line|gutter)/i.test((el.className || '').toString())) score -= 100000000;
    if (/CodeMirror/i.test((el.className || '').toString())) score -= 100000000;"""

if OLD2 in text and "_CODEMIRROR_PENALTY" not in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 已加 CodeMirror 重罚")
else:
    print("[SKIP] CodeMirror 重罚：已存在或没匹配到")

TARGET.write_text(text, encoding="utf-8")
print("完成")
