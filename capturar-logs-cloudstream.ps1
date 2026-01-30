# Capturar logs do Cloudstream

Write-Host "=== CAPTURA LOGS CLOUDSTREAM ===" -ForegroundColor Cyan
Write-Host ""

cd C:\Users\KYTHOURS\Desktop\platform-tools

# Limpar
Write-Host "1. Limpando logs..." -ForegroundColor Yellow
.\adb.exe logcat -c
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "2. NO CELULAR:" -ForegroundColor Cyan
Write-Host "   - Abrir FILME no MaxSeries" -ForegroundColor White
Write-Host "   - Clicar em PlayerEmbedAPI" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando terminar..." -ForegroundColor Yellow
Read-Host

# Capturar apenas Cloudstream
Write-Host ""
Write-Host "3. Capturando..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = "cloudstream_$timestamp.txt"

.\adb.exe logcat -d | Select-String -Pattern "cloudstream|MaxSeries|PlayerEmbedAPI|MegaEmbed|loadLinks|EXTRACT|WebView" > $logfile

$lines = (Get-Content $logfile).Count
Write-Host "Capturado: $lines linhas" -ForegroundColor Green
Write-Host "Arquivo: $logfile" -ForegroundColor Cyan
Write-Host ""

# Mostrar primeiras linhas
Write-Host "Primeiras linhas:" -ForegroundColor Yellow
Get-Content $logfile -Head 20
Write-Host ""
Write-Host "..." -ForegroundColor Gray
Write-Host ""
Write-Host "Ultimas linhas:" -ForegroundColor Yellow
Get-Content $logfile -Tail 20
