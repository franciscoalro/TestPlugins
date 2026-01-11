#!/usr/bin/env pwsh
# Verificar Dispositivo

$adb = "C:\adb\platform-tools\adb.exe"

Write-Host "Verificando dispositivos..." -ForegroundColor Green
& $adb devices

Write-Host "`nComandos para logs:" -ForegroundColor Cyan
Write-Host "Ver logs MaxSeries:" -ForegroundColor White
Write-Host "C:\adb\platform-tools\adb.exe logcat | findstr MaxSeries" -ForegroundColor Yellow

Write-Host "`nVer logs MegaEmbed:" -ForegroundColor White  
Write-Host "C:\adb\platform-tools\adb.exe logcat | findstr MegaEmbed" -ForegroundColor Yellow