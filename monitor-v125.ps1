# Monitor MaxSeries v125 - Direct API Extraction
# Data: 18/01/2026

Write-Host "=== MONITOR MAXSERIES V125 - DIRECT API ===" -ForegroundColor Cyan
Write-Host "Aguardando logs do CloudStream..." -ForegroundColor Yellow
Write-Host ""

$env:Path += ";D:\Android\platform-tools"

# Limpar logs antigos
adb logcat -c

# Filtros para v125
$filters = @(
    "PlayerEmbedAPI",
    "MegaEmbed",
    "MaxSeries",
    "Direct API",
    "WebViewResolver",
    "ExtractorLink",
    "MaxSeries-Extraction"
)

Write-Host "Filtros ativos:" -ForegroundColor Green
$filters | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Monitorar logs em tempo real
$filterPattern = ($filters -join "|")
adb logcat | Select-String -Pattern $filterPattern
