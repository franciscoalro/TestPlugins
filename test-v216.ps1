Write-Host "`n=== TESTE MAXSERIES V216 - PLAYEREMBEDAPI MANUAL ===" -ForegroundColor Cyan

# Encontrar ADB
$adbPath = (Get-ChildItem -Path C:\ -Filter "adb.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName

if (-not $adbPath) {
    Write-Host "✗ ADB não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ ADB encontrado: $adbPath" -ForegroundColor Green

# Conectar via WiFi
Write-Host "`n=== CONECTANDO VIA WIFI ===" -ForegroundColor Cyan
& $adbPath connect 192.168.0.101:33719

# Aguardar conexão
Start-Sleep -Seconds 2

# Limpar logs antigos
Write-Host "`n=== LIMPANDO LOGS ANTIGOS ===" -ForegroundColor Cyan
& $adbPath logcat -c

Write-Host "`n=== INSTRUÇÕES DE TESTE ===" -ForegroundColor Yellow
Write-Host "1. Abra o Cloudstream no dispositivo" -ForegroundColor White
Write-Host "2. Vá em Configurações → Extensions" -ForegroundColor White
Write-Host "3. Atualize MaxSeries para v216" -ForegroundColor White
Write-Host "4. Escolha uma série/filme" -ForegroundColor White
Write-Host "5. Selecione PlayerEmbedAPI como source" -ForegroundColor White
Write-Host "6. CLIQUE MANUALMENTE no botão de play quando aparecer" -ForegroundColor White
Write-Host "7. Observe os logs abaixo" -ForegroundColor White
Write-Host ""

# Capturar logs em tempo real
Write-Host "=== CAPTURANDO LOGS (Ctrl+C para parar) ===" -ForegroundColor Cyan
Write-Host "Aguardando ações no Cloudstream..." -ForegroundColor Yellow
Write-Host ""

& $adbPath logcat | Select-String -Pattern "MaxSeries|PlayerEmbed|PLAYEREMBED_RESULT|franciscoalro|Manual|WebView"
