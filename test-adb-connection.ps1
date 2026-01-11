#!/usr/bin/env pwsh
# Testar Conexão ADB

$adb = "C:\adb\platform-tools\adb.exe"

Write-Host "🧪 TESTE CONEXÃO ADB" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

Write-Host "1. Verificando ADB..." -ForegroundColor Yellow
if (Test-Path $adb) {
    Write-Host "✅ ADB encontrado: $adb" -ForegroundColor Green
} else {
    Write-Host "❌ ADB não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Listando dispositivos..." -ForegroundColor Yellow
& $adb devices

Write-Host "`n3. Testando logcat..." -ForegroundColor Yellow
Write-Host "Executando: adb logcat -d | Select-Object -First 5" -ForegroundColor Cyan

try {
    $logs = & $adb logcat -d | Select-Object -First 5
    if ($logs) {
        Write-Host "✅ Logcat funcionando!" -ForegroundColor Green
        Write-Host "Primeiras 5 linhas:" -ForegroundColor Cyan
        $logs | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    } else {
        Write-Host "⚠️ Logcat vazio ou sem permissão" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro no logcat: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 COMANDOS ÚTEIS:" -ForegroundColor Cyan
Write-Host "Listar dispositivos:" -ForegroundColor White
Write-Host "  $adb devices" -ForegroundColor Gray
Write-Host "Ver logs MaxSeries:" -ForegroundColor White  
Write-Host "  $adb logcat | findstr MaxSeries" -ForegroundColor Gray
Write-Host "Limpar logs:" -ForegroundColor White
Write-Host "  $adb logcat -c" -ForegroundColor Gray
Write-Host "Monitor em tempo real:" -ForegroundColor White
Write-Host "  .\monitor-maxseries-logs.ps1" -ForegroundColor Gray