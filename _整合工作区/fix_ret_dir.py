import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 匹配实际的旧式写法
OLD = '''                out_files = []
                for item_key, _ in expected:
                    safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    p = _versions_dir / f"{ai_key}__{safe}.md"
                    out_files.append(p)
                return out_files'''

NEW = '''                out_files = []
                ai_dir = _versions_dir / ai_key
                for item_key, _ in expected:
                    safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    p = ai_dir / f"{safe}.md"
                    out_files.append(p)
                return out_files'''

cnt = text.count(OLD)
if cnt > 0:
    text = text.replace(OLD, NEW)
    print(f"[OK] 替换 {cnt} 处旧式返回路径")
else:
    print("[FAIL] 找不到锚点")
    # 打印附近代码
    i = text.find("out_files = []")
    if i >= 0:
        print("\n附近代码：")
        print(text[i:i+400])

# 同样改 busy 分支里的
OLD2 = '''                    out_files = []
                    for item_key, _ in expected:
                        safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                        p = _versions_dir / f"{ai_key}__{safe}.md"
                        out_files.append(p)
                    return out_files'''

NEW2 = '''                    out_files = []
                    ai_dir = _versions_dir / ai_key
                    for item_key, _ in expected:
                        safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                        p = ai_dir / f"{safe}.md"
                        out_files.append(p)
                    return out_files'''

cnt2 = text.count(OLD2)
if cnt2 > 0:
    text = text.replace(OLD2, NEW2)
    print(f"[OK] 替换 {cnt2} 处 busy 分支返回路径")

# 写回
bak = TARGET.with_suffix(".py.bak_ret_dir")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print("[OK] 已写回")
