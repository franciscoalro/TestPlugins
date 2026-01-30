# Diagnóstico MegaEmbed v217
# Captura logs específicos do MegaEmbed para identificar o problema

Write-Host "🔍 DIAGNÓSTICO MEGAEMBED V217" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se ADB está disponível
$adbPath = "adb"
try {
    $null = & $adbPath version 2>&1
} catch {
    Write-Host "❌ ADB não encontrado! Instale o Android SDK Platform Tools." -ForegroundColor Red
    exit 1
}

Write-Host "✅ ADB encontrado" -ForegroundColor Green
Write-Host ""

# Verificar dispositivos conectados
Write-Host "📱 Verificando dispositivos..." -ForegroundColor Yellow
$devices = & $adbPath devices | Select-String -Pattern "device$"

if ($devices.Count -eq 0) {
    Write-Host "❌ Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host "   Conecte um dispositivo ou emulador e tente novamente." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Dispositivo conectado" -ForegroundColor Green
Write-Host ""

# Limpar logs antigos
Write-Host "🧹 Limpando logs antigos..." -ForegroundColor Yellow
& $adbPath logcat -c

Write-Host "✅ Logs limpos" -ForegroundColor Green
Write-Host ""

# Iniciar captura de logs
Write-Host "📝 Capturando logs do MegaEmbed..." -ForegroundColor Cyan
Write-Host "   Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""
Write-Host "INSTRUÇÕES:" -ForegroundColor Green
Write-Host "1. Abra o CloudStream no dispositivo" -ForegroundColor White
Write-Host "2. Navegue até MaxSeries" -ForegroundColor White
Write-Host "3. Tente reproduzir um vídeo que use MegaEmbed" -ForegroundColor White
Write-Host "4. Aguarde alguns segundos" -ForegroundColor White
Write-Host "5. Pressione Ctrl+C aqui para parar a captura" -ForegroundColor White
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_megaembed_v217_$timestamp.txt"

# Capturar logs filtrados
& $adbPath logcat -v time "*:S" `
    "MegaEmbedV9:D" `
    "WebViewPool:D" `
    "MaxSeriesProvider:D" `
    "PlayerEmbedAPI:D" `
    "VideoUrlCache:D" `
    "PersistentVideoCache:D" `
    "chromium:E" `
    "AndroidRuntime:E" | Tee-Object -FilePath $logFile

Write-Host ""
Write-Host "✅ Logs salvos em: $logFile" -ForegroundColor Green
Write-Host ""

# Análise rápida dos logs
Write-Host "🔍 ANÁLISE RÁPIDA:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

$content = Get-Content $logFile -Raw

# Verificar erros críticos
$errors = Select-String -Path $logFile -Pattern "ERROR|FATAL|Exception|crash" -CaseSensitive:$false

if ($errors.Count -gt 0) {
    Write-Host "❌ ERROS ENCONTRADOS ($($errors.Count)):" -ForegroundColor Red
    $errors | Select-Object -First 5 | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Red
    }
    Write-Host ""
}

# Verificar se MegaEmbed foi iniciado
if ($content -match "Iniciando MegaEmbed V9") {
    Write-Host "✅ MegaEmbed V9 foi iniciado" -ForegroundColor Green
} else {
    Write-Host "⚠️  MegaEmbed V9 NÃO foi iniciado" -ForegroundColor Yellow
}

# Verificar se URL foi capturada
if ($content -match "MEGA_EMBED_RESULT") {
    Write-Host "✅ URL foi capturada com sucesso" -ForegroundColor Green
} else {
    Write-Host "❌ URL NÃO foi capturada" -ForegroundColor Red
}

# Verificar timeout
if ($content -match "Timeout|timeout") {
    Write-Host "⚠️  Timeout detectado" -ForegroundColor Yellow
}

# Verificar WebView
if ($content -match "WebView") {
    Write-Host "✅ WebView foi criado" -ForegroundColor Green
}

# Verificar contexto
if ($content -match "Contexto nulo") {
    Write-Host "❌ PROBLEMA: Contexto nulo!" -ForegroundColor Red
}

Write-Host ""
Write-Host "📄 Logs completos em: $logFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Analise o arquivo de log para mais detalhes" -ForegroundColor White
Write-Host "2. Procure por 'MegaEmbedV9' para ver o fluxo completo" -ForegroundColor White
Write-Host "3. Verifique se há erros de JavaScript ou WebView" -ForegroundColor White
Write-Host ""
