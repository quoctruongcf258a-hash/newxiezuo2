from pathlib import Path
TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
print(f"含 _validate_split_coverage：{'✅' if '_validate_split_coverage' in text else '❌'}")
print(f"含 _get_expected_total_chapters：{'✅' if '_get_expected_total_chapters' in text else '❌'}")
