# Monitor MaxSeries v124 - PlayerEmbedAPI SSSRR.ORG CDN Fix
# Data: 18/01/2026

Write-Host "=== MONITOR MAXSERIES v124 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monitorando logs do MaxSeries v124..." -ForegroundColor Yellow
Write-Host "Procurando por:" -ForegroundColor White
Write-Host "  - PlayerEmbedAPI" -ForegroundColor Green
Write-Host "  - sssrr.org" -ForegroundColor Green
Write-Host "  - Video URLs" -ForegroundColor Green
Write-Host "  - Erros/Timeouts" -ForegroundColor Red
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""

# Limpar logs antigos
D:\Android\platform-tools\adb.exe logcat -c

# Monitorar logs com filtros
D:\Android\platform-tools\adb.exe logcat -v time `
    | Select-String -Pattern "PlayerEmbedAPI|sssrr\.org|MaxSeries|VideoUrl|ExtractorLink|WebView|Timeout|Error|Exception" `
    | ForEach-Object {
        $line = $_.Line
        
        # Colorir por tipo
        if ($line -match "sssrr\.org") {
            Write-Host $line -ForegroundColor Green
        }
        elseif ($line -match "PlayerEmbedAPI|VideoUrl|ExtractorLink") {
            Write-Host $line -ForegroundColor Cyan
        }
        elseif ($line -match "Error|Exception|Timeout|Falha") {
            Write-Host $line -ForegroundColor Red
        }
        elseif ($line -match "Success|capturou|interceptou") {
            Write-Host $line -ForegroundColor Yellow
        }
        else {
            Write-Host $line -ForegroundColor White
        }
    }
