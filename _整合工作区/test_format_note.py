import json, sys
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))

print("=== 写作阶段各环 format_note 返回结果 ===\n")
for ring in rings["02_写作"]["环节"]:
    # 模拟 phase_cfg：只带 code 和 name（就像 rings_items.json 里的原始结构）
    phase_cfg = {
        "code": ring.get("code", ""),
        "name": ring.get("name", ""),
        "key": ring.get("key"),  # None
    }
    note = orchestrator.format_note("写作", phase_cfg)
    print(f"--- {ring.get('code')} {ring.get('name')} ---")
    if note:
        print(note[:400] + ("..." if len(note) > 400 else ""))
    else:
        print("  ❌ 空字符串（匹配失败）")
    print()
