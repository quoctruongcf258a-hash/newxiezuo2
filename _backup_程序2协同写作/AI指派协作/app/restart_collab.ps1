# restart_collab.ps1 - restart CollabApp (程序二)，路径跟随脚本位置，拷到任意电脑可用
$app    = Split-Path -Parent $MyInvocation.MyCommand.Path   # app 目录
$root   = Split-Path -Parent $app                            # 程序根目录
$exe    = Join-Path $root "windows-use\.venv\Scripts\python.exe"
$script = Join-Path $app "collab_app.py"
$wd     = $app

# 1) kill existing collab_app instances
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like "*collab_app.py*" } |
  ForEach-Object {
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
      Write-Host "killed old PID=$($_.ProcessId)"
  }
Start-Sleep -Milliseconds 600

# 2) restart detached
Start-Process -FilePath $exe -ArgumentList $script -WorkingDirectory $wd
Write-Host "collab_app restarted"
