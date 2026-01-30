# Ver Logs em Tempo Real - v217
$adb = "C:\adb\platform-tools\adb.exe"

Write-Host "LOGS EM TEMPO REAL - MaxSeries v217" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Capturando logs de:" -ForegroundColor Yellow
Write-Host "  - MegaEmbedV9" -ForegroundColor White
Write-Host "  - WebViewPool" -ForegroundColor White
Write-Host "  - PlayerEmbedAPI" -ForegroundColor White
Write-Host "  - MaxSeriesProvider" -ForegroundColor White
Write-Host "  - VideoUrlCache" -ForegroundColor White
Write-Host "  - PersistentVideoCache" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

& $adb logcat -v time `
    MegaEmbedV9:D `
    WebViewPool:D `
    PlayerEmbedAPI:D `
    MaxSeriesProvider:D `
    VideoUrlCache:D `
    PersistentVideoCache:D `
    chromium:E `
    AndroidRuntime:E `
    *:S
