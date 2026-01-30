# Monitor rapido v125 - 60 segundos
$env:Path += ";D:\Android\platform-tools"

Write-Host "=== MONITOR V125 - 60 SEGUNDOS ===" -ForegroundColor Cyan
Write-Host "Dispositivo: Y9YP4XI7799P9LZT" -ForegroundColor Green
Write-Host ""
Write-Host "TESTE AGORA:" -ForegroundColor Yellow
Write-Host "1. Abra episodio no CloudStream" -ForegroundColor Gray
Write-Host "2. Clique em Player #1 ou #2" -ForegroundColor Gray
Write-Host ""
Write-Host "Capturando por 60 segundos..." -ForegroundColor Cyan
Write-Host ""

adb logcat -c

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v125_$timestamp.txt"

# Capturar por 60 segundos
$timeout = 60
adb logcat -T 1000 | Select-String -Pattern "PlayerEmbedAPI|MegaEmbed|MaxSeries|Direct API|WebViewResolver|ExtractorLink" | 
    ForEach-Object {
        $line = $_.Line
        Write-Host $line
        Add-Content -Path $logFile -Value $line
    } | 
    Select-Object -First 200

Write-Host ""
Write-Host "=== CAPTURA FINALIZADA ===" -ForegroundColor Green
Write-Host "Logs salvos em: $logFile" -ForegroundColor Yellow
