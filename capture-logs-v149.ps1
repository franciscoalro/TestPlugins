# Script para capturar logs ADB da v149
# MaxSeries v149 - WebView Híbrido

$ErrorActionPreference = "Stop"

Write-Host "=== CAPTURANDO LOGS ADB v149 ===" -ForegroundColor Cyan
Write-Host ""

# Caminho do ADB
$adbPath = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

# Verificar se ADB existe
if (-not (Test-Path $adbPath)) {
    Write-Host "ERRO: ADB não encontrado em $adbPath" -ForegroundColor Red
    exit 1
}

# Verificar dispositivo conectado
Write-Host "Verificando dispositivo..." -ForegroundColor Yellow
& $adbPath devices

Write-Host ""
Write-Host "=== INICIANDO CAPTURA DE LOGS ===" -ForegroundColor Green
Write-Host ""
Write-Host "Instruções:" -ForegroundColor Yellow
Write-Host "1. Abra o Cloudstream no dispositivo" -ForegroundColor White
Write-Host "2. Vá em Settings > Extensions > MaxSeries > Update" -ForegroundColor White
Write-Host "3. Aguarde atualizar para v149" -ForegroundColor White
Write-Host "4. Selecione um episódio para reproduzir" -ForegroundColor White
Write-Host "5. Aguarde o vídeo carregar (ou falhar)" -ForegroundColor White
Write-Host "6. Pressione Ctrl+C para parar a captura" -ForegroundColor White
Write-Host ""
Write-Host "Capturando logs..." -ForegroundColor Cyan
Write-Host ""

# Limpar logcat
& $adbPath logcat -c

# Timestamp para arquivo
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v149_$timestamp.txt"

# Capturar logs filtrados
& $adbPath logcat | Select-String -Pattern "MegaEmbed|CloudStream|WebView|MaxSeries" | Tee-Object -FilePath $logFile

Write-Host ""
Write-Host "=== LOGS SALVOS ===" -ForegroundColor Green
Write-Host "Arquivo: $logFile" -ForegroundColor Cyan
