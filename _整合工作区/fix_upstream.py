# fix_upstream.py — 补丁4：_read_block 注入上游文件内容（不只列路径）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    _read_block = "【读取资料（逐字读，唯一依据）】"
    if _ups:
        for _f in _ups:
            _read_block += f"\\n  · {_f}"
    else:
        _read_block += "\\n  （本环是第一个环节，无上游产物）"
'''

NEW = '''    _read_block = "【读取资料（逐字读，唯一依据）】"
    if _ups:
        for _f in _ups:
            _read_block += f"\\n  · {_f}"
        # 注入上游文件内容（长文件截断，防止 prompt 爆炸）
        _read_block += "\\n\\n【上游文件内容（已注入，可直接引用）】"
        _MAX = 4000
        for _f in _ups:
            try:
                _fp = Path(_f)
                if not _fp.exists() or not _fp.is_file():
                    continue
                _content = _fp.read_text(encoding="utf-8", errors="ignore")
                if len(_content) > _MAX:
                    _content = _content[:_MAX] + f"\\n…（已截断，全文 {len(_content)} 字，请读源文件）"
                _read_block += f"\\n\\n--- {_fp.name} ---\\n{_content}"
            except Exception:
                pass
    else:
        _read_block += "\\n  （本环是第一个环节，无上游产物）"
'''

text = TARGET.read_text(encoding="utf-8")

if "上游文件内容（已注入，可直接引用）" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_upstream")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 补丁4：上游文件内容已注入")