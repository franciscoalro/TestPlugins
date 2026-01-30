# Captura logs detalhados v149 - MegaEmbed V7
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "adb_logs_v149_detailed_$timestamp.txt"

Write-Host "=== Capturando logs detalhados v149 ===" -ForegroundColor Cyan
Write-Host "Procurando por:" -ForegroundColor Yellow
Write-Host "  - Interceptações do WebView" -ForegroundColor White
Write-Host "  - Respostas da API" -ForegroundColor White
Write-Host "  - M3U8 URLs" -ForegroundColor White
Write-Host "  - Erros e falhas" -ForegroundColor White
Write-Host ""

C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -c
Start-Sleep -Seconds 1

C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat | Select-String -Pattern "MegaEmbedV7|WebView|m3u8|ERRO|FALHA|response.body|API retornou|Nenhum link|ExtractorLink" | Tee-Object -FilePath $outputFile

Write-Host "`nLogs salvos em: $outputFile" -ForegroundColor Green
