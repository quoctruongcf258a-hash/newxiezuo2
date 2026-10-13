$file = 'F:\赛马23环整合工作室\程序2改装版\output\女王归来_test\01_规划\全书结构\versions\codebuddy\全书结构.md'
$scratch = 'F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files'

Write-Host '=== FILE STATE ==='
if (Test-Path $file) {
    $f = Get-Item $file
    Write-Host ('EXISTS  size=' + $f.Length + ' bytes  mtime=' + $f.LastWriteTime)
} else {
    Write-Host 'NOT FOUND'
}

Write-Host ''
Write-Host '=== POLL 12 x 2s (watch for external truncation) ==='
for ($i = 1; $i -le 12; $i++) {
    if (Test-Path $file) {
        $len = (Get-Item $file).Length
        Write-Host ("poll $i  size=$len  " + (Get-Date -Format 'HH:mm:ss'))
    } else {
        Write-Host ("poll $i  FILE MISSING  " + (Get-Date -Format 'HH:mm:ss'))
    }
    Start-Sleep -Seconds 2
}

Write-Host ''
Write-Host '=== RECENT SCRATCH TASK FILES ==='
Get-ChildItem $scratch -Filter 'task__规划*' | Sort-Object LastWriteTime -Descending | Select-Object -First 20 Name, LastWriteTime, Length | Format-Table -AutoSize | Out-String -Width 220 | Write-Host
