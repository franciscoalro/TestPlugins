#!/usr/bin/env pwsh
# Setup ADB Simples

Write-Host "Instalando ADB..." -ForegroundColor Green

# Criar pasta
$adbPath = "C:\adb"
New-Item -ItemType Directory -Path $adbPath -Force

# Download
$url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
$zip = "$adbPath\platform-tools.zip"

Write-Host "Baixando ADB..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $url -OutFile $zip

Write-Host "Extraindo..." -ForegroundColor Yellow
Expand-Archive -Path $zip -DestinationPath $adbPath -Force

Write-Host "Testando..." -ForegroundColor Yellow
& "$adbPath\platform-tools\adb.exe" version

Write-Host "ADB instalado em: $adbPath\platform-tools\" -ForegroundColor Green
Write-Host "Para usar: $adbPath\platform-tools\adb.exe devices" -ForegroundColor Cyan