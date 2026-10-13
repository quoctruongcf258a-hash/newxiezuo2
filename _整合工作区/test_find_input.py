import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab, _FIND_INPUT_JS

t = CDPTab(9231, "doubao-chat")
box = t.js(_FIND_INPUT_JS)
print("找到的输入框：")
print(box)
if box:
    print(f"\n坐标：({box['x']}, {box['y']})")
    print(f"class：{box['cls']}")
    print(f"候选数：{box['n']}")
    if box['y'] > 0:
        print("\n✅ 补丁生效：选中的是屏幕内输入框")
    else:
        print("\n❌ 补丁没生效：还是选中了屏幕外的 CodeMirror")
