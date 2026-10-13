# -*- coding: utf-8 -*-
"""
生成 Windows 启动器 .bat
名称：32流程版（F 盘改装版正式定名）

关键修复（此前"全部打不开"的根因）：
  bat 必须写 GBK 编码 + CRLF。若用 UTF-8，cmd 按 ANSI(GBK) 解析会乱码并破坏语法。

运行环境状态（2026-10-11 已重建完成并实测）：
  F 副本自带独立 venv = windows-use\\.venv（857M / 413 包 / Python 3.13.14）
  含 PySide6、psutil、win32api、pyautogui、websocket、requests -> 已实测主界面正常弹窗
  不再依赖原盘 venv（原盘仅作兜底）

解释器选择（已实测验证）：
  主界面 collab_app.py   -> PySide6，用 F 副本 venv（优先），残缺才回退原盘
  登记台 gui_launcher.py -> tkinter，venv 无 tkinter；用系统 Python314（实测可弹出）

接入规模：第一版设计源 37 环全部落地（规划23 + 写作4 + 润色1 + 质检9）
"""
import os

DST = r"F:\赛马23环整合工作室\程序2改装版"
NAME = "32流程版"

ORIG_VENV = r"C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe"
SYS_PY314 = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"

HEAD = """@echo off
cd /d "%~dp0"
"""

def write(name, body):
    path = os.path.join(DST, name)
    with open(path, "w", encoding="gbk", newline="\r\n", errors="replace") as f:
        f.write(body)
    return path

# ---------------------------------------------------------------- 主界面
MAIN = HEAD + f"""title {NAME} - Collab Writing Main UI

set "VENV=%~dp0windows-use\\.venv"
set "VPY=%VENV%\\Scripts\\python.exe"
set "SRC=LOCAL"

rem 只有 python.exe 且 PySide6 齐全才算可用环境，否则回退原盘（避免用到复制一半的残缺 venv）
if not exist "%VPY%" goto USE_ORIG
if not exist "%VENV%\\Lib\\site-packages\\PySide6" goto USE_ORIG
goto RUN

:USE_ORIG
set "VPY={ORIG_VENV}"
set "SRC=ORIG"

:RUN
if not exist "%VPY%" (
  echo.
  echo [ERROR] No usable python runtime found.
  echo   looked for: %VENV%\\Scripts\\python.exe
  echo   fallback  : {ORIG_VENV}
  echo.
  pause
  exit /b 1
)

echo ============================================
echo   {NAME}  /  Main UI
echo   Runtime : %VPY%
echo   Code    : %CD%
echo ============================================
echo.

"%VPY%" "app\\collab_app.py"

echo.
echo ============ EXIT CODE = %errorlevel% ============
echo Non-zero means crashed; the Traceback above is the reason.
echo.
pause
"""

# ---------------------------------------------------------------- 登记台
REG = HEAD + f"""title {NAME} - Roster Console (23 rings)

rem 登记台用 tkinter；实测 venv 的 python 不带 tkinter，故优先系统 Python314
set "VPY={SYS_PY314}"
if not exist "%VPY%" set "VPY=%~dp0windows-use\\.venv\\Scripts\\python.exe"
if not exist "%VPY%" set "VPY={ORIG_VENV}"

if not exist "%VPY%" (
  echo.
  echo [ERROR] No usable python runtime found.
  echo.
  pause
  exit /b 1
)

echo ============================================
echo   {NAME}  /  Roster Console
echo   Runtime : %VPY%
echo   Code    : %CD%
echo ============================================
echo.

"%VPY%" "windows-use\\_scratch\\gui_launcher.py"

echo.
echo ============ EXIT CODE = %errorlevel% ============
pause
"""

# ---------------------------------------------------------------- 命令行菜单
# 注意：原盘 windows-use/run.bat 是坏的——它调用 orchestrator.py，但该脚本在 _scratch/ 子目录，
#      根目录并没有，所以原盘那个菜单点了会报"找不到文件"。这里重建一版指向正确的。
CLI = HEAD + f"""title {NAME} - Command Line Menu

set "VENV=%~dp0windows-use\\.venv"
set "VPY=%VENV%\\Scripts\\python.exe"
set "SRC=LOCAL"
if not exist "%VPY%" goto C_ORIG
if not exist "%VENV%\\Lib\\site-packages\\psutil" goto C_ORIG
goto C_MENU

:C_ORIG
set "VPY={ORIG_VENV}"
set "SRC=ORIG"

:C_MENU
if not exist "%VPY%" (
  echo [ERROR] No usable python runtime found.
  pause
  exit /b 1
)

cd /d "%~dp0windows-use\\_scratch"

:MENU
cls
echo ============================================
echo   {NAME}  /  37-ring engine
echo   (planning 23 + writing 4 + polish 1 + QC 9)
echo ============================================
echo   [1] 校验今日阵容
echo   [2] 跑 规划 - 试运行 dry-run
echo   [3] 跑 规划 - 正式运行
echo   [4] 赛马记分榜
echo   [5] 查看今日阵容
echo   [0] 退出
echo ============================================
echo.
set "C="
set /p C=选择: 

if "%C%"=="1" "%VPY%" orchestrator.py --check-session & goto DONE
if "%C%"=="2" "%VPY%" orchestrator.py --program 规划 --dry-run & goto DONE
if "%C%"=="3" "%VPY%" orchestrator.py --program 规划 & goto DONE
if "%C%"=="4" "%VPY%" orchestrator.py --board & goto DONE
if "%C%"=="5" "%VPY%" session.py show & goto DONE
if "%C%"=="0" goto EOF
echo 无效选择
pause
goto MENU

:DONE
echo.
echo 完成。
pause
goto MENU

:EOF
exit /b 0
"""

# ---------------------------------------------------------------- 自检
DIAG = HEAD + f"""title {NAME} - Self Check (no GUI)

set "VENV=%~dp0windows-use\\.venv"
set "VPY=%VENV%\\Scripts\\python.exe"
set "SRC=LOCAL"
if not exist "%VPY%" goto D_ORIG
if not exist "%VENV%\\Lib\\site-packages\\PySide6" goto D_ORIG
goto D_RUN

:D_ORIG
set "VPY={ORIG_VENV}"
set "SRC=ORIG"

:D_RUN
echo ============================================
echo   {NAME} SELF CHECK
echo ============================================
echo.
echo [1] Runtime:
echo     %VPY%
if not exist "%VPY%" (echo     STATUS = MISSING) else (echo     STATUS = FOUND)
if "%SRC%"=="LOCAL" (echo     SOURCE = 独立环境 F副本 .venv) else (echo     SOURCE = 回退原盘 venv)
echo.
echo [2] Packages needed by Main UI:
"%VPY%" -c "import importlib.util as u;print('    python OK');[print('    ',m,'OK' if u.find_spec(m) else 'MISSING') for m in ['PySide6','psutil','win32api','pyautogui']]"
echo.
echo [3] Rules / 37 rings:
"%VPY%" -c "import json;d=json.load(open(r'%CD%\\rules\\phases.json',encoding='utf-8'));s=d['环节'];[print('    ',k,len(v)) for k,v in s.items()];print('     设计源37环合计 =',sum(len(s[k]) for k in ['01_规划','02_写作','03_去AI','04_审核']))"
echo.
echo [4] Entries:
if exist "%CD%\\app\\collab_app.py" (echo     app\\collab_app.py FOUND) else (echo     app\\collab_app.py MISSING)
if exist "%CD%\\windows-use\\_scratch\\gui_launcher.py" (echo     _scratch\\gui_launcher.py FOUND) else (echo     _scratch\\gui_launcher.py MISSING)
echo.
echo [5] tkinter (for roster console):
"{SYS_PY314}" -c "import tkinter;print('    system python314 tkinter OK',tkinter.TkVersion)"
echo.
echo ============================================
pause
"""

for name, body in [
    ("启动_主界面.bat", MAIN),
    ("启动_登记台.bat", REG),
    ("启动_命令行菜单.bat", CLI),
    ("环境自检.bat", DIAG),
]:
    p = write(name, body)
    print("written:", p)

print("\n--- verify: decode as GBK, expect 0 mojibake lines ---")
for name in ["启动_主界面.bat", "启动_登记台.bat", "启动_命令行菜单.bat", "环境自检.bat"]:
    b = open(os.path.join(DST, name), "rb").read()
    t = b.decode("gbk", errors="replace")
    bad = sum(1 for l in t.splitlines() if "\ufffd" in l)
    print(f"  {name}: mojibake={bad}, CRLF={b.count(chr(13).encode()+chr(10).encode())}")
