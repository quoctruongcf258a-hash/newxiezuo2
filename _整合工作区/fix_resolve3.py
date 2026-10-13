import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# ── 精确匹配旧函数（包括结尾的两个换行）──
OLD = '''def _resolve_ai_name(ai_key):
    """把 AI 的 key（如 workbuddy）解析成 mix_send 认识的真实名字（如 WorkBuddy）。
    mix_send 的 CDP_APPS 用的是首字母大写，gemini 例外。
    """
    if not ai_key:
        return ai_key
    try:
        import sys as _s
        _wu = HERE.parent
        if str(_wu) not in _s.path:
            _s.path.insert(0, str(_wu))
        from mix_send import _lookup, CDP_APPS, PYA_APPS
        # 1. 原 key 直查
        if _lookup(ai_key):
            return ai_key
        # 2. 遍历所有已配置名字，大小写不敏感匹配
        for apps in (CDP_APPS, PYA_APPS):
            try:
                for k in apps.keys():
                    if k.lower() == ai_key.lower():
                        return k
            except Exception:
                continue
    except Exception:
        pass
    return ai_key'''

NEW = '''def _resolve_ai_name(ai_key):
    """把 AI 的 key（如 workbuddy）解析成 mix_send 认识的真实名字（如 WorkBuddy）。
    优先从 today.json 读 label（与 CDP_APPS 一致），fallback 用硬编码表。
    """
    if not ai_key:
        return ai_key

    # 1. 从 today.json 读 key → label 映射
    try:
        import json as _json
        candidates = [
            HERE.parent / "_scratch" / "today.json",
            HERE.parent / "today.json",
        ]
        for tj in candidates:
            if not tj.exists():
                continue
            data = _json.loads(tj.read_text(encoding="utf-8"))
            for item in data.get("opened") or []:
                if (item.get("key") or "").lower() == ai_key.lower():
                    return item.get("label") or ai_key
    except Exception:
        pass

    # 2. 硬编码 fallback
    _MAP = {
        "workbuddy": "WorkBuddy",
        "doubao":    "Doubao",
        "codebuddy": "CodeBuddy",
        "quest":     "QUEST",
        "gemini":    "gemini",
        "qianwen":   "Qianwen",
        "deepseek":  "DeepSeek",
        "kimi":      "Kimi",
        "tongyi":    "通义千问",
        "yuanbao":   "元宝",
        "zcode":     "ZCode",
    }
    return _MAP.get(ai_key.lower(), ai_key)'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_resolve3")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已替换 _resolve_ai_name")
else:
    print("[FAIL] 找不到旧函数")
    # 打印附近看看
    i = text.find("def _resolve_ai_name")
    if i >= 0:
        print("附近代码（前 200 字符）：")
        print(repr(text[i:i+300]))
