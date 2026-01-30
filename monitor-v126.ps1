# Monitor MaxSeries v126 - WebView Melhorado
# Data: 18/01/2026

Write-Host "=== MONITOR MAXSERIES V126 ===" -ForegroundColor Cyan
Write-Host "WebView Melhorado: 120s timeout + tryPlay + Pattern 6" -ForegroundColor Yellow
Write-Host ""

# Verificar dispositivo conectado
$device = adb devices | Select-String "device$" | Select-Object -First 1
if (-not $device) {
    Write-Host "ERRO: Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host "Conecte o dispositivo e tente novamente." -ForegroundColor Yellow
    exit 1
}

Write-Host "Dispositivo conectado: $device" -ForegroundColor Green
Write-Host ""

# Limpar logs antigos
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
adb logcat -c

Write-Host ""
Write-Host "=== MONITORANDO LOGS (Ctrl+C para parar) ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "O QUE PROCURAR:" -ForegroundColor Yellow
Write-Host "  MegaEmbed:" -ForegroundColor White
Write-Host "    - 'Direct API capturou' = API direta funcionou" -ForegroundColor Green
Write-Host "    - 'WebView JS capturou' = WebView funcionou (v126)" -ForegroundColor Green
Write-Host "    - 'Timeout apos 1200 tentativas' = Timeout 120s" -ForegroundColor Red
Write-Host "    - 'Nenhuma URL capturada' = Falhou" -ForegroundColor Red
Write-Host ""
Write-Host "  PlayerEmbedAPI:" -ForegroundColor White
Write-Host "    - 'Capturado sssrr.org' = Sucesso" -ForegroundColor Green
Write-Host "    - 'Timeout' = Falhou" -ForegroundColor Red
Write-Host ""

# Monitorar logs em tempo real
adb logcat | Select-String -Pattern "MegaEmbed|PlayerEmbed|MaxSeries|ExtractorLink" -CaseSensitive:$false
