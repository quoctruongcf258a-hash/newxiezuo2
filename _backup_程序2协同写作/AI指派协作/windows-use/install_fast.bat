@echo off
chcp 65001 >nul
REM Windows-Use 环境安装（自动化层）
REM 用本地 Python 3.13.12 + 华为云镜像建 .venv，并安装 windows-use。
REM 若在 X-VPN 后面，取消注释代理那行并改端口。

set "PY313=C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"

cd /d "%~dp0"

echo ============================================================
echo   [1/3] 创建虚拟环境 .venv
echo ============================================================
%PY313% -m venv .venv
if errorlevel 1 (
  echo [ERR] 用 3.13.12 创建 venv 失败。
  pause
  exit /b 1
)

call .venv\Scripts\activate

echo.
echo ============================================================
echo   [2/3] 安装依赖（windows-use / python-dotenv / mistralai^<2）
echo ============================================================
pip install --upgrade pip

REM --- 方案 A：华为云镜像（先试这个）---
pip install -r requirements.txt -i https://repo.huaweicloud.com/repository/pypi/simple

REM --- 方案 B：若 A 仍然慢，改用 X-VPN 代理（取消注释并改端口）---
REM pip install -r requirements.txt -i https://repo.huaweicloud.com/repository/pypi/simple --proxy http://127.0.0.1:7890

echo.
echo ============================================================
echo   [3/3] 自检
echo ============================================================
python -c "import windows_use; print('[OK] windows-use', windows_use.__version__)"
if errorlevel 1 echo [FAIL] windows-use 导入失败，请查看上面的报错

REM 图形界面需要 tkinter；本 venv 用的 3.13.12 精简版可能不带。
REM 不必修 .venv —— run_gui.bat 会自动改用系统里带 tkinter 的 Python 打开界面，
REM 而流水线本身始终用本 .venv 运行。
".venv\Scripts\python.exe" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo [提示] 本 venv 不含 tkinter。这不影响运行：
  echo        图形界面请用 run_gui.bat（会自动挑选带 tkinter 的 Python）；
  echo        命令行请用 run.bat。
) else (
  echo [OK] 本 venv 自带 tkinter，run_gui.bat 会直接用它。
)

echo.
echo 安装流程结束。下一步：双击 run_gui.bat 登记今日阵容。
pause
