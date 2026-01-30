# Captura de Logs para Debug
# Execute este comando e DEPOIS tente reproduzir um video no CloudStream

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CAPTURA DE LOGS - DEBUG v156" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs limpos. Pronto para capturar!" -ForegroundColor Green
Write-Host ""
Write-Host "INSTRUCOES:" -ForegroundColor Yellow
Write-Host "1. Escolha um episodio no CloudStream" -ForegroundColor White
Write-Host "2. Clique para reproduzir" -ForegroundColor White
Write-Host "3. AGUARDE ate dar erro ou funcionar" -ForegroundColor White
Write-Host "4. Pressione qualquer tecla aqui" -ForegroundColor White
Write-Host ""
Write-Host "Aguardando voce tentar reproduzir..." -ForegroundColor Cyan
Read-Host "Pressione ENTER apos tentar reproduzir"

Write-Host ""
Write-Host "Capturando logs..." -ForegroundColor Yellow

$logFile = "debug_playback_$(Get-Date -Format 'HHmmss').txt"
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -d > $logFile

Write-Host "OK Logs salvos em: $logFile" -ForegroundColor Green
Write-Host ""

# Analisar logs
Write-Host "Analisando erros..." -ForegroundColor Yellow
Write-Host ""

$errors = Select-String -Path $logFile -Pattern "ERROR|ERRO|Failed|Exception|❌" | Select-Object -Last 20
$megaembed = Select-String -Path $logFile -Pattern "MegaEmbed" | Select-Object -Last 30
$maxseries = Select-String -Path $logFile -Pattern "MaxSeries" | Select-Object -Last 30

Write-Host "=== ERROS ENCONTRADOS ===" -ForegroundColor Red
$errors | ForEach-Object { Write-Host $_.Line -ForegroundColor Red }

Write-Host ""
Write-Host "=== LOGS DO MEGAEMBED ===" -ForegroundColor Cyan
$megaembed | ForEach-Object { Write-Host $_.Line -ForegroundColor Cyan }

Write-Host ""
Write-Host "=== LOGS DO MAXSERIES ===" -ForegroundColor Yellow  
$maxseries | ForEach-Object { Write-Host $_.Line -ForegroundColor Yellow }

Write-Host ""
Write-Host "Arquivo completo: $logFile" -ForegroundColor Green
