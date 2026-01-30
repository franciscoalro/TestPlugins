#!/usr/bin/env pwsh
# Monitor MaxSeries v122 - PlayerEmbedAPI JS Filter Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MaxSeries v122 ADB Monitor" -ForegroundColor Cyan
Write-Host "  PlayerEmbedAPI JS Filter Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se ADB está disponível
$adbPath = Get-Command adb -ErrorAction SilentlyContinue
if (-not $adbPath) {
    Write-Host "❌ ADB não encontrado!" -ForegroundColor Red
    Write-Host "Instale o ADB ou adicione ao PATH" -ForegroundColor Yellow
    exit 1
}

# Verificar dispositivo conectado
Write-Host "[1/3] Verificando dispositivo..." -ForegroundColor Yellow
$devices = adb devices | Select-String "device$"
if ($devices.Count -eq 0) {
    Write-Host "❌ Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host "Conecte um dispositivo Android via USB ou WiFi" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Dispositivo conectado" -ForegroundColor Green
Write-Host ""

# Limpar logs antigos
Write-Host "[2/3] Limpando logs antigos..." -ForegroundColor Yellow
adb logcat -c
Write-Host "✅ Logs limpos" -ForegroundColor Green
Write-Host ""

# Iniciar monitoramento
Write-Host "[3/3] Monitorando logs do MaxSeries..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 Filtros ativos:" -ForegroundColor Cyan
Write-Host "   - PlayerEmbedAPI" -ForegroundColor White
Write-Host "   - Extração de URLs" -ForegroundColor White
Write-Host "   - Filtro .js" -ForegroundColor White
Write-Host "   - Erros e avisos" -ForegroundColor White
Write-Host ""
Write-Host "📱 Agora no CloudStream:" -ForegroundColor Yellow
Write-Host "   1. Busque 'Terra de Pecados'" -ForegroundColor White
Write-Host "   2. Selecione um episódio" -ForegroundColor White
Write-Host "   3. Clique em PlayerEmbedAPI" -ForegroundColor White
Write-Host "   4. Aguarde o carregamento" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Monitorar logs com filtros específicos
adb logcat | Select-String -Pattern "PlayerEmbedAPI|MaxSeries|ExtractorLink|WebView|storage\.googleapis|core\.bundle|\.js|VideoUrl|Extraction" | ForEach-Object {
    $line = $_.Line
    
    # Colorir por tipo de mensagem
    if ($line -match "storage\.googleapis\.com") {
        Write-Host $line -ForegroundColor Green
    }
    elseif ($line -match "core\.bundle|\.js") {
        Write-Host $line -ForegroundColor Red
    }
    elseif ($line -match "ERROR|FATAL|Exception") {
        Write-Host $line -ForegroundColor Red
    }
    elseif ($line -match "WARN|Warning") {
        Write-Host $line -ForegroundColor Yellow
    }
    elseif ($line -match "SUCCESS|Captured|ExtractorLink") {
        Write-Host $line -ForegroundColor Green
    }
    elseif ($line -match "PlayerEmbedAPI|Extraction") {
        Write-Host $line -ForegroundColor Cyan
    }
    else {
        Write-Host $line -ForegroundColor White
    }
}
