from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

print("=" * 70)
print("检查补丁是否打上")
print("=" * 70)
print(f"  含 _validate_split_coverage：{'✅' if '_validate_split_coverage' in text else '❌'}")
print(f"  含 _get_expected_total_chapters：{'✅' if '_get_expected_total_chapters' in text else '❌'}")

# 找 _maybe_extract_split 的真实签名
import re
m = re.search(r"def _maybe_extract_split\([^)]*\):", text)
if m:
    print(f"\n_maybe_extract_split 签名：{m.group(0)}")

# 看它的写入段是否已改
i = text.find("def _maybe_extract_split")
if i >= 0:
    seg = text[i:i+1500]
    print(f"\n前 1500 字：")
    print(seg)
