#!/usr/bin/env pwsh
# Verificar ADB

Write-Host "Verificando ADB..." -ForegroundColor Green

$adb = "C:\adb\platform-tools\adb.exe"

if (Test-Path $adb) {
    Write-Host "ADB encontrado!" -ForegroundColor Green
    & $adb devices
} else {
    Write-Host "ADB nao encontrado. Execute: ./install-adb.ps1" -ForegroundColor Red
}