Write-Host "🔍 Capturando logs MaxSeries v219..." -ForegroundColor Cyan
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v219_$timestamp.txt"

Write-Host "📝 Salvando em: $logFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Aguardando logs... (Ctrl+C para parar)" -ForegroundColor Green
Write-Host ""

adb logcat -c
adb logcat | Select-String -Pattern "MaxSeries|PlayerEmbedAPI|WebView" | Tee-Object -FilePath $logFile
