# fix_tab_pick.py — 选页时优先 Slate 聊天框（避免误选右侧文件编辑器）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''                box = self.js(_FIND_INPUT_JS)
                if box:
                    # 内部页（launcher/background）仅作兜底，有正常页面时绝不优先
                    rank = 0 if not _internal(p) else -1
                    found.append((rank, int(box.get("area") or 0), p, ws, box))
                else:
                    ws.close()
                    self.ws = None
'''

NEW = '''                box = self.js(_FIND_INPUT_JS)
                if box:
                    # 内部页（launcher/background）仅作兜底，有正常页面时绝不优先
                    rank = 0 if not _internal(p) else -1
                    # 优先 Slate 聊天输入框（避免误选右侧文件编辑器里的大 textarea）
                    try:
                        slate = 1 if self._is_slate_input() else 0
                    except Exception:
                        slate = 0
                    found.append((rank, slate, int(box.get("area") or 0), p, ws, box))
                else:
                    ws.close()
                    self.ws = None
'''

if "优先 Slate 聊天输入框" in text:
    print("已改过1")
else:
    if OLD not in text:
        print("找不到锚点1，先看当前代码")
    else:
        text = text.replace(OLD, NEW, 1)
        print("✔ 补丁A：选页时优先 Slate 聊天框")

OLD2 = '''        if found:
            found.sort(key=lambda x: (x[0], x[1]), reverse=True)
            rank, area, p, ws, box = found[0]
            self.ws = ws
            self.mid = 0
            self.title = p.get("title", "")
            for _, _, _p, _ws, _ in found[1:]:
'''

NEW2 = '''        if found:
            # 排序键：(rank, slate, area) —— slate=1 的聊天框优先
            found.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
            rank, slate, area, p, ws, box = found[0]
            self.ws = ws
            self.mid = 0
            self.title = p.get("title", "")
            for _, _, _, _p, _ws, _ in found[1:]:
'''

if "slate=1 的聊天框优先" in text:
    print("已改过2")
elif OLD2 not in text:
    print("找不到锚点2，先看当前代码")
else:
    text = text.replace(OLD2, NEW2, 1)
    print("✔ 补丁B：排序键加入 slate")

# 保存
if "优先 Slate 聊天输入框" in text or "slate=1 的聊天框优先" in text:
    bak = TARGET.with_suffix(".py.bak_tabpick")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("已保存")
else:
    print("没有改动")