@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 多 AI 协作写作流水线 · 命令行菜单

REM ── 命令行兜底入口（没有图形环境时用）。
REM    自动化层需要 .venv（已装 windows-use）；只看阵容/校验则任意 Python 均可。

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================================
echo   多 AI 协作写作流水线
echo ============================================================
echo   [1] 查看今日阵容（候选池 + 已登记）
echo   [2] 校验今日阵容（人数/拼接者/跨厂）
echo   [3] 探测今日 AI 是否可用（登录/额度）
echo   [4] 一键套用预设阵容（写入 today.json）
echo   ----------------------------------------------------------
echo   [5] 跑 规划   （一次性，产出章纲）
echo   [6] 跑 写作   （按章）
echo   [7] 跑 润色   （按章）
echo   [8] 跑 质检   （按章；每 10 章自动追加连贯性复检）
echo   [9] 手动连贯性复检（按章）
echo   [0] 赛马记分榜（打分统计 / 冠亚季军 / 环节×AI 对照）
echo ============================================================
choice /c 1234567890 /n /m "请选择: "

if errorlevel 10 goto BOARD
if errorlevel 9 goto RC
if errorlevel 8 goto QC
if errorlevel 7 goto POLISH
if errorlevel 6 goto WRITE
if errorlevel 5 goto PLAN
if errorlevel 4 goto PRESET
if errorlevel 3 goto PROBE
if errorlevel 2 goto CHECK
if errorlevel 1 goto SHOW

:SHOW
"%PY%" session.py show
goto END

:CHECK
"%PY%" orchestrator.py --check-session
goto END

:PROBE
set "MODE="
choice /c YN /n /m "真实探测？(Y=真跑, N=只看任务) "
if errorlevel 2 set "MODE=--dry-run"
"%PY%" orchestrator.py --probe %MODE%
goto END

:PRESET
echo.
echo 下面是候选池与可用预设（预设行以 key 开头）：
"%PY%" session.py show
echo.
set /p PKEY=输入预设 key（如 steady5）: 
"%PY%" session.py preset %PKEY%
goto END

:PLAN
call :ASKMODE
"%PY%" orchestrator.py --program 规划 %DRY%
goto END

:WRITE
call :ASKCHAP
call :ASKMODE
"%PY%" orchestrator.py --program 写作 --chapter %CHAP% %DRY%
goto END

:POLISH
call :ASKCHAP
call :ASKMODE
"%PY%" orchestrator.py --program 润色 --chapter %CHAP% %DRY%
goto END

:QC
call :ASKCHAP
call :ASKMODE
"%PY%" orchestrator.py --program 质检 --chapter %CHAP% %DRY%
goto END

:RC
call :ASKCHAP
"%PY%" orchestrator.py --recheck --chapter %CHAP% --dry-run
goto END

:BOARD
echo.
echo 看哪个程序？ [1]全场 [2]规划 [3]写作 [4]润色 [5]质检 [6]解除淘汰 [7]清空记分榜
choice /c 1234567 /n /m "请选择: "
if errorlevel 7 goto B_RESET
if errorlevel 6 goto B_RESTORE
if errorlevel 5 "%PY%" orchestrator.py --board 质检 & goto END
if errorlevel 4 "%PY%" orchestrator.py --board 润色 & goto END
if errorlevel 3 "%PY%" orchestrator.py --board 写作 & goto END
if errorlevel 2 "%PY%" orchestrator.py --board 规划 & goto END
"%PY%" orchestrator.py --board
goto END

:B_RESTORE
set /p AKEY=输入要解除淘汰的 AI key（如 tongyi）: 
"%PY%" scoreboard.py restore %AKEY%
goto END

:B_RESET
choice /c YN /n /m "确定清空整张记分榜？(Y=清空, N=取消) "
if errorlevel 2 goto END
"%PY%" scoreboard.py reset
goto END

:ASKCHAP
set "CHAP="
set /p CHAP=章号（四位，如 0057）: 
if "%CHAP%"=="" set "CHAP=0057"
exit /b 0

:ASKMODE
set "DRY="
choice /c YN /n /m "正式运行？(Y=真实操控AI, N=试运行) "
if errorlevel 2 set "DRY=--dry-run"
exit /b 0

:END
echo.
echo 完成。
pause
