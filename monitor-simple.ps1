#!/usr/bin/env pwsh
# Monitor MaxSeries Logs - Simple Version

$adb = "C:\adb\platform-tools\adb.exe"

Write-Host "MONITOR MAXSERIES LOGS" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green

# Check connected devices
Write-Host "Checking connected devices..." -ForegroundColor Yellow
& $adb devices

$devices = & $adb devices | Select-String "device$"
if ($devices.Count -eq 0) {
    Write-Host "No device found!" -ForegroundColor Red
    exit 1
}

Write-Host "Device connected!" -ForegroundColor Green

# Clear old logs
Write-Host "Clearing old logs..." -ForegroundColor Yellow
& $adb logcat -c

Write-Host "Monitoring MaxSeries logs..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "=" * 60

# Monitor specific MaxSeries logs
& $adb logcat | Select-String -Pattern "MaxSeries|MegaEmbed|CloudStream" | ForEach-Object {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = $_.Line
    
    # Color logs by type
    if ($line -match "ERROR") {
        Write-Host "[$timestamp] $line" -ForegroundColor Red
    } elseif ($line -match "SUCCESS") {
        Write-Host "[$timestamp] $line" -ForegroundColor Green
    } elseif ($line -match "WARNING") {
        Write-Host "[$timestamp] $line" -ForegroundColor Yellow
    } elseif ($line -match "MegaEmbed") {
        Write-Host "[$timestamp] $line" -ForegroundColor Cyan
    } else {
        Write-Host "[$timestamp] $line" -ForegroundColor White
    }
}