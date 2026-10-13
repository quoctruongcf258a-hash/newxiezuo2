Write-Host "=====系统信息====="
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber | Format-List
Write-Host "=====CPU====="
Get-CimInstance Win32_Processor | Select-Object Name, MaxClockSpeed | Format-List
Write-Host "=====内存====="
$m = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB
Write-Host "Total Memory: $m GB"
Write-Host "=====显卡====="
Get-CimInstance Win32_VideoController | Select-Object Name | Format-List
