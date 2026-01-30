$adb = "D:\Android\platform-tools\adb.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MaxSeries v121 ADB Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check device
Write-Host "[1] Verificando dispositivo..." -ForegroundColor Yellow
& $adb devices
Write-Host ""

# Check CloudStream version
Write-Host "[2] Verificando CloudStream..." -ForegroundColor Yellow
$csVersion = & $adb shell dumpsys package com.lagradost.cloudstream3 | Select-String "versionName"
Write-Host $csVersion
Write-Host ""

# Check MaxSeries plugin
Write-Host "[3] Verificando plugins instalados..." -ForegroundColor Yellow
$pluginPath = "/data/data/com.lagradost.cloudstream3/files/plugins"
& $adb shell "ls -la $pluginPath 2>/dev/null || echo 'Pasta de plugins não encontrada'"
Write-Host ""

# Clear logs
Write-Host "[4] Limpando logs..." -ForegroundColor Yellow
& $adb logcat -c
Write-Host "✅ Logs limpos" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agora:" -ForegroundColor Yellow
Write-Host "1. Abra o CloudStream no dispositivo" -ForegroundColor White
Write-Host "2. Vá em Configurações → Extensões" -ForegroundColor White
Write-Host "3. Atualize o MaxSeries para v121" -ForegroundColor White
Write-Host "4. Teste uma série (ex: Terra de Pecados)" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER para começar a monitorar os logs..." -ForegroundColor Green
Read-Host

Write-Host ""
Write-Host "Monitorando logs (Ctrl+C para parar)..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Monitor logs
& $adb logcat | Select-String -Pattern "MaxSeries|PlayerEmbed|franciscoalro|ExtractorLink|WebView.*maxseries|cloudstream.*plugin" -CaseSensitive:$false
