# Script ultra-leve para monitorar o plugin MaxSeries
# Use este script para ver o que acontece no celular em tempo real

$ADB = "C:\adb\platform-tools\adb.exe"

Write-Host "--------------------------------------------------" -ForegroundColor Cyan
Write-Host "🔍 MONITOR DE LOGS - MAXSERIES v79" -ForegroundColor Cyan
Write-Host "--------------------------------------------------" -ForegroundColor Cyan
Write-Host "Status: Aguardando atividade no CloudStream..." -ForegroundColor Gray
Write-Host "Pressione Ctrl+C para parar." -ForegroundColor DarkGray
Write-Host ""

# Limpa o buffer antigo para não confundir
& $ADB logcat -c

# Inicia o monitoramento filtrado pelas tags do plugin
& $ADB logcat -v time -s MaxSeriesProvider:D MegaEmbedExtractor:D PlayerEmbedAPI:D
