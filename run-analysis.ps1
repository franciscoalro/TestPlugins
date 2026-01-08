# Script para executar análise completa do MaxSeries
Write-Host "🦎 INICIANDO ANÁLISE AUTOMÁTICA MAXSERIES" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. Verificar se setup foi feito
if (-not (Test-Path "geckodriver.exe")) {
    Write-Host "⚙️ Executando setup inicial..." -ForegroundColor Yellow
    & .\setup-geckodriver.ps1
}

# 2. Executar análise Python
Write-Host "🔍 Iniciando análise com GeckoDriver..." -ForegroundColor Green
python analyze-maxseries.py

# 3. Verificar resultados
if (Test-Path "maxseries_analysis.json") {
    Write-Host "✅ Análise concluída com sucesso!" -ForegroundColor Green
    
    # Mostrar resumo dos resultados
    $analysis = Get-Content "maxseries_analysis.json" | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "📊 RESUMO DA ANÁLISE:" -ForegroundColor Cyan
    
    if ($analysis.series_analysis) {
        $series = $analysis.series_analysis
        Write-Host "📺 SÉRIE ANALISADA:" -ForegroundColor Yellow
        Write-Host "  URL: $($series.page_info.url)" -ForegroundColor White
        Write-Host "  Título: $($series.page_info.title)" -ForegroundColor White
        Write-Host "  Temporadas DooPlay: $($series.episodes.dooplay_seasons.Count)" -ForegroundColor White
        Write-Host "  Estruturas alternativas: $($series.episodes.alternative_structures.Count)" -ForegroundColor White
        Write-Host "  Iframes encontrados: $($series.players.iframes.Count)" -ForegroundColor White
        Write-Host "  Botões de player: $($series.players.player_buttons.Count)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "📄 ARQUIVOS GERADOS:" -ForegroundColor Cyan
    Write-Host "  - maxseries_analysis.json (análise completa)" -ForegroundColor White
    Write-Host "  - scraper_suggestions.json (sugestões de código)" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🔧 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
    Write-Host "1. Revise os arquivos JSON gerados" -ForegroundColor White
    Write-Host "2. Use as informações para melhorar o scraper" -ForegroundColor White
    Write-Host "3. Execute .\auto-fix-and-release.ps1 para aplicar correções" -ForegroundColor White
    
} else {
    Write-Host "❌ Análise falhou. Verifique os logs acima." -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Para análise personalizada:" -ForegroundColor Cyan
Write-Host "python analyze-maxseries.py" -ForegroundColor White