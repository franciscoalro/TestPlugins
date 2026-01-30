# Captura logs do ADB para análise
# Executa por 60 segundos

Write-Host "=== CAPTURANDO LOGS DO ADB ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dispositivo conectado:" -ForegroundColor Yellow
D:\Android\platform-tools\adb.exe devices
Write-Host ""
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
D:\Android\platform-tools\adb.exe logcat -c
Write-Host ""
Write-Host "Capturando logs por 60 segundos..." -ForegroundColor Green
Write-Host "Abra um episódio no CloudStream agora!" -ForegroundColor Yellow
Write-Host ""

# Capturar logs
$outputFile = "adb_logs_v124_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
D:\Android\platform-tools\adb.exe logcat -v time -d > $outputFile

Write-Host "Logs salvos em: $outputFile" -ForegroundColor Green
Write-Host ""
Write-Host "Analisando logs..." -ForegroundColor Yellow

# Análise rápida
$content = Get-Content $outputFile -Raw

Write-Host ""
Write-Host "=== RESUMO ===" -ForegroundColor Cyan

if ($content -match "PlayerEmbedAPI") {
    Write-Host "✓ PlayerEmbedAPI encontrado nos logs" -ForegroundColor Green
} else {
    Write-Host "✗ PlayerEmbedAPI NÃO encontrado" -ForegroundColor Red
}

if ($content -match "sssrr\.org") {
    Write-Host "✓ sssrr.org encontrado nos logs" -ForegroundColor Green
    $matches = [regex]::Matches($content, "https?://[^\s]+sssrr\.org[^\s]+")
    Write-Host "  URLs encontradas: $($matches.Count)" -ForegroundColor Cyan
} else {
    Write-Host "✗ sssrr.org NÃO encontrado" -ForegroundColor Red
}

if ($content -match "Timeout|timeout") {
    Write-Host "⚠ Timeout detectado" -ForegroundColor Yellow
}

if ($content -match "Error|Exception") {
    Write-Host "⚠ Erros detectados" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Arquivo completo: $outputFile" -ForegroundColor White
