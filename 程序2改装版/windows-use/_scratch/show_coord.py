import json
c = json.load(open(r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json", encoding="utf-8"))
for k in ["CodeBuddy", "Qianwen"]:
    if k in c:
        print(f"{k}:")
        print(f"  input_pos   = {c[k].get('input_pos')}")
        print(f"  window_rect = {c[k].get('window_rect')}")
        print(f"  input_rel   = {c[k].get('input_rel')}")
    else:
        print(f"{k}: 无")
