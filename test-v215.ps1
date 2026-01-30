Write-Host "`n=== TESTE MAXSERIES V215 ===" -ForegroundColor Cyan

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

# Aguardar um pouco
Start-Sleep -Seconds 2

# Capturar logs em tempo real
Write-Host "`n=== CAPTURANDO LOGS (Ctrl+C para parar) ===" -ForegroundColor Cyan
Write-Host "Aguardando ações no Cloudstream..." -ForegroundColor Yellow
Write-Host ""

& $adbPath logcat -c  # Limpar logs antigos
& $adbPath logcat | Select-String -Pattern "MaxSeries|PlayerEmbed|franciscoalro|Checksum"
