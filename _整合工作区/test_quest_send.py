# test_quest_send.py — 在 QUEST 已粘贴状态下，测 Enter 能不能发出去
import sys, time
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab, _LEFT_JS

tab = CDPTab(9224)
tab.ai = "QUEST"

# 1. 看现在输入框有多少字
left = tab.js(_LEFT_JS)
print(f"输入框当前字数: {left}")

if left and left > 100:
    print("尝试按 Enter 发送...")
    tab.cmd("Input.dispatchKeyEvent", type="rawKeyDown",
            windowsVirtualKeyCode=13, code="Enter", key="Enter")
    time.sleep(0.08)
    tab.cmd("Input.dispatchKeyEvent", type="char", text="\r")
    time.sleep(0.08)
    tab.cmd("Input.dispatchKeyEvent", type="keyUp",
            windowsVirtualKeyCode=13, code="Enter", key="Enter")
    time.sleep(2.0)

    left2 = tab.js(_LEFT_JS)
    print(f"Enter 后输入框字数: {left2}")

    if left2 and left2 > 100:
        print("Enter 未生效，尝试点击绿色 ↑ 按钮...")
        # 找绿色发送按钮（右下角，绿色）
        btn = tab.js("""
        (() => {
            for (const b of document.querySelectorAll('button, [role="button"]')) {
                const r = b.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) continue;
                // 右下角 + 绿色
                const x = r.x + r.width/2, y = r.y + r.height/2;
                const bg = getComputedStyle(b).backgroundColor;
                if (x > 500 && y > 400 && (bg.includes('34, 197') || bg.includes('green') || bg.includes('rgb(22, 163'))) {
                    return {x: Math.round(x), y: Math.round(y), bg, cls: (b.className||'').slice(0,60)};
                }
            }
            return null;
        })()
        """)
        print(f"找到绿色按钮: {btn}")
        if btn:
            tab.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=btn["x"], y=btn["y"])
            time.sleep(0.1)
            tab.cmd("Input.dispatchMouseEvent", type="mousePressed", x=btn["x"], y=btn["y"], button="left", clickCount=1)
            time.sleep(0.08)
            tab.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=btn["x"], y=btn["y"], button="left", clickCount=1)
            time.sleep(2.0)
            left3 = tab.js(_LEFT_JS)
            print(f"按钮点击后输入框字数: {left3}")