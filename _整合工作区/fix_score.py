# fix_score.py — 修正 _SCORE_JS：Slate 聊天框绝对优先 + 去掉文件头 BOM
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")

# 用 utf-8-sig 读，自动吃掉 BOM
raw = TARGET.read_bytes()
if raw.startswith(b"\xef\xbb\xbf"):
    print("检测到 BOM，去掉")
    raw = raw[3:]
text = raw.decode("utf-8")

OLD = '''    // 明确的聊天语义
    if (/提问|问题|发送消息|消息|对话|ask|message|prompt|send|chat/i.test(meta)) score += 5000000;
    out.push({el: el, score: score});
'''

NEW = '''    // 明确的聊天语义
    if (/提问|问题|发送消息|消息|对话|ask|message|prompt|send|chat/i.test(meta)) score += 5000000;
    // Slate 富文本编辑器 = 聊天输入框（WorkBuddy/QUEST 等），绝对优先
    // 文件编辑器的 sc-root-editable 不是 Slate，会被这行彻底压过
    if (el.getAttribute('data-slate-editor') === 'true'
        || el.querySelector('[data-slate-editor=true]')) score += 100000000;
    // role=textbox 也是聊天框特征
    if (el.getAttribute('role') === 'textbox') score += 20000000;
    // 明确的编辑器/文件容器，重罚
    if (/root-editable|file-edit|code-editor|monaco|editor-container/i.test(
            (el.className || '').toString())) score -= 100000000;
    out.push({el: el, score: score});
'''

if "Slate 富文本编辑器 = 聊天输入框" in text:
    print("已改过")
elif OLD not in text:
    print("找不到 _SCORE_JS 锚点")
    i = text.find("明确的聊天语义")
    if i >= 0:
        print(text[i-100:i+400])
else:
    bak = TARGET.with_suffix(".py.bak_score")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    # 保存时用 utf-8（不带 BOM）
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已修正 _SCORE_JS（Slate + 排除编辑器）")
    print("✔ 已去掉文件头 BOM")