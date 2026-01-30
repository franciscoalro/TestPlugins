# Captura de Logs MaxSeries v217
# Conecta via ADB WiFi e captura logs do MegaEmbed e WebViewPool

Write-Host "CAPTURA DE LOGS v217" -ForegroundColor Cyan
Write-Host ""

# Tentar encontrar ADB
$adbPaths = @(
    "C:\adb\platform-tools\adb.exe",
    "adb",
    "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe",
    "$env:USERPROFILE\AppData\Local\Android\Sdk\platform-tools\adb.exe"
)

$adb = $null
foreach ($path in $adbPaths) {
    try {
        $null = & $path version 2>&1
        $adb = $path
        break
    } catch {}
}

if (-not $adb) {
    Write-Host "ADB nao encontrado!" -ForegroundColor Red
    Write-Host "Instale Android SDK Platform Tools" -ForegroundColor Yellow
    exit 1
}

Write-Host "ADB encontrado: $adb" -ForegroundColor Green
Write-Host ""

# Conectar
Write-Host "Conectando a 192.168.0.101:39471..." -ForegroundColor Yellow
& $adb connect 192.168.0.101:39471
Write-Host ""

# Verificar dispositivos
Write-Host "Dispositivos conectados:" -ForegroundColor Yellow
& $adb devices
Write-Host ""

# Limpar logs
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Capturar logs
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v217_$timestamp.txt"

Write-Host "Capturando logs..." -ForegroundColor Cyan
Write-Host "Arquivo: $logFile" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

& $adb logcat -v time "*:S" `
    "MegaEmbedV9:D" `
    "WebViewPool:D" `
    "PlayerEmbedAPI:D" `
    "MaxSeriesProvider:D" `
    "VideoUrlCache:D" `
    "PersistentVideoCache:D" `
    "chromium:E" `
    "AndroidRuntime:E" | Tee-Object -FilePath $logFile
