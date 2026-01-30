# Monitor ADB em Tempo Real - MaxSeries v124
# Pressione Ctrl+C para parar

$adb = "D:\Android\platform-tools\adb.exe"

Write-Host "=== MONITOR ADB TEMPO REAL - v124 ===" -ForegroundColor Cyan
Write-Host ""

# Verificar dispositivo
Write-Host "Verificando dispositivo..." -ForegroundColor Yellow
$devices = & $adb devices
if ($devices -match "device$") {
    Write-Host "✓ Dispositivo conectado" -ForegroundColor Green
} else {
    Write-Host "✗ Nenhum dispositivo conectado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c

Write-Host ""
Write-Host "=== MONITORANDO LOGS ===" -ForegroundColor Cyan
Write-Host "Procurando por:" -ForegroundColor White
Write-Host "  • PlayerEmbedAPI" -ForegroundColor Green
Write-Host "  • sssrr.org" -ForegroundColor Green
Write-Host "  • ExtractorLink" -ForegroundColor Green
Write-Host "  • Erros/Timeouts" -ForegroundColor Red
Write-Host ""
Write-Host "Abra um episódio no CloudStream agora!" -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""
Write-Host "─" * 80
Write-Host ""

# Monitorar em tempo real
& $adb logcat -v time | ForEach-Object {
    $line = $_
    
    # Filtrar apenas linhas relevantes
    if ($line -match "PlayerEmbedAPI|sssrr\.org|MaxSeries|ExtractorLink|WebView.*video|Timeout|Falha|capturou|interceptou|Error.*MaxSeries") {
        
        $timestamp = Get-Date -Format "HH:mm:ss"
        
        # Colorir por tipo
        if ($line -match "sssrr\.org") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host "🎯 SSSRR.ORG: " -NoNewline -ForegroundColor Green
            Write-Host $line -ForegroundColor White
        }
        elseif ($line -match "PlayerEmbedAPI.*capturou|interceptou") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host "✓ SUCESSO: " -NoNewline -ForegroundColor Yellow
            Write-Host $line -ForegroundColor White
        }
        elseif ($line -match "ExtractorLink") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host "📺 LINK: " -NoNewline -ForegroundColor Cyan
            Write-Host $line -ForegroundColor White
        }
        elseif ($line -match "Timeout|Falha|Error") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host "✗ ERRO: " -NoNewline -ForegroundColor Red
            Write-Host $line -ForegroundColor White
        }
        elseif ($line -match "PlayerEmbedAPI|MaxSeries") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host "ℹ INFO: " -NoNewline -ForegroundColor Blue
            Write-Host $line -ForegroundColor White
        }
    }
}
