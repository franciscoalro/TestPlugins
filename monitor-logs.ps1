#!/usr/bin/env pwsh
# Monitor MaxSeries Logs

$adb = "C:\adb\platform-tools\adb.exe"

Write-Host "Monitorando logs do MaxSeries..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Green

# Limpar logs antigos
& $adb logcat -c

# Monitorar logs
& $adb logcat | Select-String -Pattern "MaxSeries|MegaEmbed|PlayerEmbed|CloudStream" | ForEach-Object {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $($_.Line)" -ForegroundColor White
}