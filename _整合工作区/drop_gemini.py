import json
from pathlib import Path

today = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\today.json")
data = json.loads(today.read_text(encoding="utf-8"))

# 备份
bak = today.with_suffix(".json.bak_no_gemini")
if not bak.exists():
    import shutil
    shutil.copy(today, bak)
    print("已备份：", bak.name)

# 摘掉 gemini
before = [x["key"] for x in data.get("opened", [])]
data["opened"] = [x for x in data.get("opened", []) if x.get("key") != "gemini"]
after = [x["key"] for x in data["opened"]]

# merge_app 若为 gemini，改成 workbuddy
if data.get("merge_app") == "gemini":
    data["merge_app"] = "workbuddy"

today.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("原阵容：", before)
print("新阵容：", after)
print("merge_app：", data.get("merge_app"))
