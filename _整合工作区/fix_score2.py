# fix_score2.py — 去 BOM + 改 _SCORE_JS（用行内锚点，兼容 \r\n）
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")

# 1) 读原始字节
raw = TARGET.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
    print("检测到 BOM，去掉")

# 2) 统一行尾为 \n，处理
text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

# 3) 用行内锚点做替换（比块级更稳）
ANCHOR = "if (/提问|问题|发送消息|消息|对话|ask|message|prompt|send|chat/i.test(meta)) score += 5000000;"

if "Slate 富文本编辑器 = 聊天输入框" in text:
    print("已改过")
elif ANCHOR not in text:
    print("找不到锚点，打印附近内容：")
    i = text.find("对话|ask|message")
    if i >= 0:
        print(repr(text[i-100:i+200]))
else:
    # 在锚点行后面插入新逻辑
    INSERT = ANCHOR + """
    // Slate 富文本编辑器 = 聊天输入框（WorkBuddy/QUEST 等），绝对优先
    if (el.getAttribute('data-slate-editor') === 'true'
        || el.querySelector('[data-slate-editor=true]')) score += 100000000;
    if (el.getAttribute('role') === 'textbox') score += 20000000;
    // 文件编辑器容器，重罚
    if (/root-editable|file-edit|code-editor|monaco|editor-container/i.test(
            (el.className || '').toString())) score -= 100000000;"""
    text = text.replace(ANCHOR, INSERT, 1)
    print("✔ 已在 _SCORE_JS 插入 Slate 优先 + 编辑器重罚")

# 4) 写回（无 BOM）
TARGET.write_text(text, encoding="utf-8")
print("✔ 文件已写回（无 BOM）")