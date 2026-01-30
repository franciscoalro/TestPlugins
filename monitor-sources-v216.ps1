Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        MONITOR DE SOURCES - MAXSERIES V216                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Encontrar ADB
$adbPath = (Get-ChildItem -Path C:\ -Filter "adb.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName

if (-not $adbPath) {
    Write-Host "✗ ADB não encontrado!" -ForegroundColor Red
    exit 1
}

# Conectar
Write-Host "📱 Conectando em 192.168.0.106:34699..." -ForegroundColor Yellow
& $adbPath connect 192.168.0.106:34699 | Out-Null
Start-Sleep -Seconds 1

# Verificar conexão
$devices = & $adbPath devices
if ($devices -match "192.168.0.106:34699") {
    Write-Host "✓ Conectado!" -ForegroundColor Green
} else {
    Write-Host "✗ Falha na conexão!" -ForegroundColor Red
    exit 1
}

# Limpar logs
Write-Host "`n🧹 Limpando logs antigos..." -ForegroundColor Yellow
& $adbPath logcat -c

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              MONITORAMENTO ATIVO                               ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📋 O QUE OBSERVAR:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. 🎬 Provider carregado (v216)" -ForegroundColor White
Write-Host "  2. 🔗 loadLinks chamado" -ForegroundColor White
Write-Host "  3. 📺 Sources encontradas (MyVidPlay, MegaEmbed, PlayerEmbedAPI, etc)" -ForegroundColor White
Write-Host "  4. ⚡ Extractors tentados" -ForegroundColor White
Write-Host "  5. ✅ URLs capturadas" -ForegroundColor White
Write-Host "  6. ❌ Erros (se houver)" -ForegroundColor White
Write-Host ""
Write-Host "💡 DICA: Abra um episódio no Cloudstream agora!" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Monitorar logs com cores
& $adbPath logcat | ForEach-Object {
    $line = $_
    
    # Provider carregado
    if ($line -match "MAXSERIES PROVIDER.*CARREGADO") {
        Write-Host $line -ForegroundColor Green
    }
    # loadLinks
    elseif ($line -match "LOADLINKS CHAMADO|loadLinks:") {
        Write-Host $line -ForegroundColor Cyan
    }
    # Sources encontradas
    elseif ($line -match "Sources encontradas|data-source|Processando source") {
        Write-Host $line -ForegroundColor Yellow
    }
    # Extractors
    elseif ($line -match "Tentando.*Extractor|PlayerEmbed|MegaEmbed|MyVidPlay|DoodStream|StreamTape|Mixdrop|Filemoon") {
        Write-Host $line -ForegroundColor Magenta
    }
    # URLs capturadas
    elseif ($line -match "capturou|RESULT:|URL CAPTURADA|\.m3u8|\.mp4|sssrr\.org") {
        Write-Host $line -ForegroundColor Green
    }
    # Erros
    elseif ($line -match "ERROR|Erro|Failed|falhou|❌") {
        Write-Host $line -ForegroundColor Red
    }
    # Sucesso
    elseif ($line -match "SUCCESS|Sucesso|✅|Links encontrados") {
        Write-Host $line -ForegroundColor Green
    }
    # MaxSeries geral
    elseif ($line -match "MaxSeries|franciscoalro") {
        Write-Host $line -ForegroundColor White
    }
}
