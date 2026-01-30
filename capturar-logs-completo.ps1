# Capturar logs ADB completos

Write-Host "=== CAPTURA LOGS ADB COMPLETO ===" -ForegroundColor Cyan
Write-Host ""

cd C:\Users\KYTHOURS\Desktop\platform-tools

# Limpar logs
Write-Host "1. Limpando logs..." -ForegroundColor Yellow
.\adb.exe logcat -c
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "2. AGORA NO CELULAR:" -ForegroundColor Cyan
Write-Host "   - Abrir FILME no MaxSeries" -ForegroundColor White
Write-Host "   - Clicar em PlayerEmbedAPI" -ForegroundColor White
Write-Host "   - Aguardar resultado" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando terminar..." -ForegroundColor Yellow
Read-Host

# Capturar TUDO
Write-Host ""
Write-Host "3. Capturando logs completos..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = "adb_completo_$timestamp.txt"

.\adb.exe logcat -d > $logfile

$size = (Get-Item $logfile).Length / 1KB
Write-Host "Logs salvos: $logfile ($([math]::Round($size, 2)) KB)" -ForegroundColor Green
Write-Host ""

# Contar linhas relevantes
$maxseriesLines = (Select-String -Path $logfile -Pattern "MaxSeries").Count
$playerembedLines = (Select-String -Path $logfile -Pattern "PlayerEmbedAPI").Count

Write-Host "Linhas MaxSeries: $maxseriesLines" -ForegroundColor $(if($maxseriesLines -gt 0){"Green"}else{"Red"})
Write-Host "Linhas PlayerEmbedAPI: $playerembedLines" -ForegroundColor $(if($playerembedLines -gt 0){"Green"}else{"Red"})
Write-Host ""

if ($maxseriesLines -eq 0) {
    Write-Host "AVISO: Nenhum log do MaxSeries encontrado!" -ForegroundColor Red
    Write-Host "Verifique se:" -ForegroundColor Yellow
    Write-Host "  - MaxSeries v222 esta instalado" -ForegroundColor White
    Write-Host "  - Voce abriu um conteudo do MaxSeries" -ForegroundColor White
    Write-Host "  - O app nao crashou" -ForegroundColor White
}

Write-Host ""
Write-Host "Arquivo: $logfile" -ForegroundColor Cyan
