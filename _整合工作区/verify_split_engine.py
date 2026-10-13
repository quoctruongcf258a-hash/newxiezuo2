import sys
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

try:
    import orchestrator
    print("=== import 成功 ===")
    for fn in ["_extract_json_block", "_get_split_spec", "_maybe_extract_split", "_do_produce_split"]:
        print(f"  {fn}: {'存在' if hasattr(orchestrator, fn) else '缺失'}")
    print(f"  SPLIT_PRODUCERS: {getattr(orchestrator, 'SPLIT_PRODUCERS', '缺失')}")
    print(f"  SPLIT_SOURCES:   {getattr(orchestrator, 'SPLIT_SOURCES', '缺失')}")

    # 检查 __main__ 顺序
    text = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py").read_text(encoding="utf-8")
    i_func = text.find("def _do_produce_split")
    i_main = text.find('\nif __name__ == "__main__":')
    print(f"\n  _do_produce_split 在 __main__ 前：{'是 [OK]' if 0 <= i_func < i_main else '否 [FAIL]'}")
except SyntaxError as e:
    print(f"[SYNTAX ERROR] {e}")
except Exception as e:
    print(f"[ERROR] {e}")
