@echo off
cd /d "%~dp0"
title 32流程版 - Self Check (no GUI)

set "VENV=%~dp0windows-use\.venv"
set "VPY=%VENV%\Scripts\python.exe"
set "SRC=LOCAL"
if not exist "%VPY%" goto D_ORIG
if not exist "%VENV%\Lib\site-packages\PySide6" goto D_ORIG
goto D_RUN

:D_ORIG
set "VPY=C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe"
set "SRC=ORIG"

:D_RUN
echo ============================================
echo   32流程版 SELF CHECK
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
"%VPY%" -c "import json;d=json.load(open(r'%CD%\rules\phases.json',encoding='utf-8'));s=d['环节'];[print('    ',k,len(v)) for k,v in s.items()];print('     设计源37环合计 =',sum(len(s[k]) for k in ['01_规划','02_写作','03_去AI','04_审核']))"
echo.
echo [4] Entries:
if exist "%CD%\app\collab_app.py" (echo     app\collab_app.py FOUND) else (echo     app\collab_app.py MISSING)
if exist "%CD%\windows-use\_scratch\gui_launcher.py" (echo     _scratch\gui_launcher.py FOUND) else (echo     _scratch\gui_launcher.py MISSING)
echo.
echo [5] tkinter (for roster console):
"C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe" -c "import tkinter;print('    system python314 tkinter OK',tkinter.TkVersion)"
echo.
echo ============================================
pause
