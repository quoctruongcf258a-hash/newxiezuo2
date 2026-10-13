# fix_open_instr.py — 从备份恢复 tasks.py，然后精准重写 _open_instruction
import shutil
from pathlib import Path

TASKS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
BAK = TASKS.with_suffix(".py.bak_fmode2")

# 1) 从备份恢复
if not BAK.exists():
    print("✗ 备份不存在:", BAK)
    raise SystemExit(1)
shutil.copy(BAK, TASKS)
print(f"✔ 已从 {BAK.name} 恢复 tasks.py")

# 2) 读出来，重写 _open_instruction
text = TASKS.read_text(encoding="utf-8")

START = "def _open_instruction(app: dict) -> str:"
start = text.find(START)
if start < 0:
    print("✗ 找不到 _open_instruction")
    raise SystemExit(1)

# 找到下一个顶格 def
end = text.find("\ndef ", start + len(START))
if end < 0:
    end = len(text)

NEW_FUNC = '''def _open_instruction(app: dict) -> str:
    """生成「打开并聚焦这个 AI」的指令。electron/web 走不同路径。"""
    label = app.get("label") or app.get("key") or "目标程序"
    # electron / desktop 类型 → 桌面程序
    _t = (app.get("类型") or app.get("form") or "").lower()
    if _t in ("electron", "desktop") or _form_of(app) == "desktop":
        exe = (app.get("target") or "").strip()
        if exe and exe.lower().endswith(".exe"):
            return (
                f"启动或聚焦「{label}」桌面程序（可执行文件：{exe}）。"
                f"若已在运行，直接切换到它的主窗口并置前；"
                f"若未安装或启动失败，停下并报告「{label} 不可用」，不要尝试其它程序。"
            )
        return (
            f"启动或聚焦「{label}」桌面程序（它在系统中的识别方式：{exe}）。"
            f"若已在运行，直接切换到其主窗口并置前；找不到就停下并报告不可用。"
        )
    # web 类型 → 浏览器
    url = (app.get("target") or "").strip()
    browser = (app.get("browser") or "EDGE").upper()
    return (
        f"打开 {browser} 浏览器，导航到网址 {url}，等待页面加载完成。"
        f"确认页面处于「可输入提问」状态（输入框可见、可点击）；"
        f"若要求登录而当前未登录，停下并报告「{label} 需先登录」，不要尝试输入账号密码。"
    )

'''

text = text[:start] + NEW_FUNC + text[end+1:]  # end+1 跳过前面的 \n
TASKS.write_text(text, encoding="utf-8")
print("✔ 已重写 _open_instruction")