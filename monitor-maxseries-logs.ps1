#!/usr/bin/env pwsh
# Monitor MaxSeries Logs em Tempo Real

$adb = "C:\adb\platform-tools\adb.exe"

Write-Host "📱 MONITOR MAXSERIES LOGS" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Verificar se dispositivo está conectado
Write-Host "🔍 Verificando dispositivos conectados..." -ForegroundColor Yellow
& $adb devices

$devices = & $adb devices | Select-String "device$"
if ($devices.Count -eq 0) {
    Write-Host "❌ Nenhum dispositivo encontrado!" -ForegroundColor Red
    Write-Host "📋 CHECKLIST:" -ForegroundColor Yellow
    Write-Host "1. Celular conectado via USB?" -ForegroundColor White
    Write-Host "2. Depuração USB ativada?" -ForegroundColor White
    Write-Host "3. Autorização concedida no celular?" -ForegroundColor White
    exit 1
}

Write-Host "✅ Dispositivo conectado!" -ForegroundColor Green

# Limpar logs antigos
Write-Host "🗑️ Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c

Write-Host "🎯 Monitorando logs do MaxSeries..." -ForegroundColor Cyan
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host "=" * 60

# Monitorar logs específicos do MaxSeries
& $adb logcat | Select-String -Pattern "MaxSeries|MegaEmbed|CloudStream" | ForEach-Object {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = $_.Line
    
    # Colorir logs por tipo
    if ($line -match "ERROR|❌") {
        Write-Host "[$timestamp] $line" -ForegroundColor Red
    } elseif ($line -match "SUCCESS|✅") {
        Write-Host "[$timestamp] $line" -ForegroundColor Green
    } elseif ($line -match "WARNING|⚠️") {
        Write-Host "[$timestamp] $line" -ForegroundColor Yellow
    } elseif ($line -match "MegaEmbed") {
        Write-Host "[$timestamp] $line" -ForegroundColor Cyan
    } else {
        Write-Host "[$timestamp] $line" -ForegroundColor White
    }
}